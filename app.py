from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st

from src.recommendations import get_recommendation, get_score_explanation
from src.scoring import SCORE_ORDER, compare_to_benchmark


DATA_PATH = Path(__file__).parent / "data" / "benchmark_data.csv"

METRIC_LABELS = {
    "utilization": "Utilization",
    "revenue_per_employee": "Revenue per employee",
    "ebitda_margin": "EBITDA margin",
    "margin": "Margin",
    "productivity": "Productivity",
    "growth": "Growth",
    "digital_maturity": "Digital maturity",
    "employee_retention": "Employee retention",
    "ai_adoption": "AI adoption",
    "customer_satisfaction": "Customer satisfaction",
    "project_delivery_success": "Project delivery success",
}

SIZE_ORDER = ["1-50", "50-250", "250-1000", "1000+"]

DEFAULT_METRIC_ORDER = ["margin", "productivity", "growth", "digital_maturity"]

INDUSTRY_METRIC_ORDER = {
    "Consulting": [
        "utilization",
        "revenue_per_employee",
        "ebitda_margin",
        "growth",
        "employee_retention",
        "ai_adoption",
        "customer_satisfaction",
        "project_delivery_success",
    ]
}


@st.cache_data
def load_benchmark_data() -> pd.DataFrame:
    """Load benchmark data and validate the expected MVP schema."""
    data = pd.read_csv(DATA_PATH)
    required_columns = {
        "industry",
        "company_size",
        "metric",
        "unit",
        "p25",
        "p50",
        "p75",
    }
    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Benchmark data is missing required columns: {missing}")

    for column in ["p25", "p50", "p75"]:
        data[column] = pd.to_numeric(data[column], errors="raise")

    return data


def metric_label(metric: str) -> str:
    return METRIC_LABELS.get(metric, metric.replace("_", " ").title())


def format_value(value: float, unit: str) -> str:
    if unit == "%":
        return f"{value:.1f}%"
    if unit == "$k/employee":
        return f"${value:,.0f}k / employee"
    if unit == "score 1-5":
        return f"{value:.1f} / 5"
    if unit == "score 1-10":
        return f"{value:.1f} / 10"
    return f"{value:,.1f}"


def value_input_settings(metric: str, unit: str) -> dict:
    if unit == "score 1-5":
        return {"min_value": 0.0, "max_value": 5.0, "step": 0.1, "format": "%.1f"}
    if unit == "score 1-10":
        return {"min_value": 0.0, "max_value": 10.0, "step": 0.1, "format": "%.1f"}
    if unit == "$k/employee":
        return {"min_value": 0.0, "step": 10.0, "format": "%.0f"}
    return {"min_value": 0.0, "step": 0.5, "format": "%.1f"}


def build_result_rows(selected_rows: pd.DataFrame, user_values: dict[str, float]) -> list[dict]:
    result_rows = []

    for _, benchmark in selected_rows.iterrows():
        metric = benchmark["metric"]
        unit = benchmark["unit"]
        result = compare_to_benchmark(user_values[metric], benchmark)
        status = result["status"]

        result_rows.append(
            {
                "Metric": metric_label(metric),
                "Your value": format_value(result["user_value"], unit),
                "Market median": format_value(result["market_median"], unit),
                "Top quartile": format_value(result["top_quartile"], unit),
                "Status": status,
                "Recommended AI improvement lever": get_recommendation(
                    metric=metric,
                    status=status,
                    industry=benchmark["industry"],
                ),
            }
        )

    return result_rows


def metric_sort_key(industry: str, metric: str) -> int:
    metric_order = INDUSTRY_METRIC_ORDER.get(industry, DEFAULT_METRIC_ORDER)
    if metric in metric_order:
        return metric_order.index(metric)
    return len(metric_order)


def build_excel_export(results_table: pd.DataFrame, industry: str, company_size: str) -> bytes:
    output = BytesIO()
    setup_table = pd.DataFrame(
        {
            "Field": ["Industry", "Company size"],
            "Value": [industry, company_size],
        }
    )

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        setup_table.to_excel(writer, sheet_name="Setup", index=False)
        results_table.to_excel(writer, sheet_name="Benchmark results", index=False)

        for sheet_name, worksheet in writer.sheets.items():
            worksheet.freeze_panes(1, 0)
            worksheet.set_column(0, 0, 24)
            worksheet.set_column(1, 5, 20)
            worksheet.set_column(6, 6, 72)

    return output.getvalue()


st.set_page_config(
    page_title="AI Benchmarking Tool",
    layout="wide",
)

st.title("AI Benchmarking Tool")
st.caption("Compare your company performance against sample market benchmark percentiles.")

try:
    benchmark_data = load_benchmark_data()
except FileNotFoundError:
    st.error(f"Benchmark data file was not found at {DATA_PATH}.")
    st.stop()
except ValueError as error:
    st.error(str(error))
    st.stop()

industries = sorted(benchmark_data["industry"].dropna().unique())
company_sizes = [size for size in SIZE_ORDER if size in benchmark_data["company_size"].unique()]

with st.sidebar:
    st.header("Benchmark setup")
    industry = st.selectbox("Industry", industries)
    company_size = st.selectbox("Company size", company_sizes)

filtered_data = benchmark_data[
    (benchmark_data["industry"] == industry)
    & (benchmark_data["company_size"] == company_size)
].copy()

if filtered_data.empty:
    st.warning("No benchmark data exists for this industry and company size.")
    st.stop()

available_metrics = sorted(
    filtered_data["metric"].unique(),
    key=lambda metric: metric_sort_key(industry, metric),
)

with st.sidebar:
    selected_metrics = st.multiselect(
        "Metrics",
        options=available_metrics,
        default=available_metrics,
        format_func=metric_label,
    )

if not selected_metrics:
    st.info("Select at least one metric in the sidebar to start benchmarking.")
    st.stop()

selected_rows = filtered_data[filtered_data["metric"].isin(selected_metrics)]

st.subheader("Enter your values")
with st.form("benchmark_form"):
    user_values: dict[str, float] = {}
    input_columns = st.columns(min(len(selected_rows), 4))

    for index, (_, benchmark) in enumerate(selected_rows.iterrows()):
        metric = benchmark["metric"]
        unit = benchmark["unit"]
        column = input_columns[index % len(input_columns)]
        label = f"{metric_label(metric)} ({unit})"

        user_values[metric] = column.number_input(
            label,
            value=float(benchmark["p50"]),
            help=f"Market median is {format_value(float(benchmark['p50']), unit)}.",
            **value_input_settings(metric, unit),
        )

    submitted = st.form_submit_button("Run benchmark", type="primary")

if not submitted:
    st.info("Enter your values and run the benchmark to see results.")
    st.stop()

st.subheader("Benchmark comparison")
results = build_result_rows(selected_rows, user_values)
results_table = pd.DataFrame(results)
st.dataframe(results_table, use_container_width=True, hide_index=True)

st.subheader("Score guide")
score_columns = st.columns(len(SCORE_ORDER))
for column, status in zip(score_columns, SCORE_ORDER):
    column.markdown(f"**{status}**")
    column.write(get_score_explanation(status))

st.subheader("Recommendations")
for row in results:
    st.markdown(f"**{row['Metric']}:** {row['Recommended AI improvement lever']}")

st.subheader("Export")
file_safe_industry = industry.lower().replace(" ", "_")
file_safe_size = company_size.replace("+", "plus").replace("-", "_")
st.download_button(
    label="Download Excel report",
    data=build_excel_export(results_table, industry, company_size),
    file_name=f"ai_benchmark_{file_safe_industry}_{file_safe_size}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
