from io import BytesIO
from pathlib import Path

import altair as alt
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

STATUS_COLORS = {
    "Below market": "#d64545",
    "Emerging": "#f2a93b",
    "Competitive": "#2f80ed",
    "Leading": "#1f9d55",
}

DISPLAY_COLUMNS = [
    "Metric",
    "Your value",
    "Market median",
    "Top quartile",
    "Gap to median",
    "Gap to top quartile",
    "Progress to top quartile",
    "Status",
    "Recommended AI improvement lever",
]


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


def format_gap(value: float, unit: str) -> str:
    if unit == "%":
        return f"{value:+.1f} pp"
    if unit == "$k/employee":
        return f"{value:+,.0f}k / employee"
    if unit in {"score 1-5", "score 1-10"}:
        return f"{value:+.1f} points"
    return f"{value:+,.1f}"


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
        user_value = result["user_value"]
        market_median = result["market_median"]
        top_quartile = result["top_quartile"]
        gap_to_median = user_value - market_median
        gap_to_top_quartile = user_value - top_quartile
        progress_to_top_quartile = (
            (user_value / top_quartile) * 100 if top_quartile else 0
        )

        result_rows.append(
            {
                "Metric": metric_label(metric),
                "Your value": format_value(user_value, unit),
                "Market median": format_value(market_median, unit),
                "Top quartile": format_value(top_quartile, unit),
                "Gap to median": format_gap(gap_to_median, unit),
                "Gap to top quartile": format_gap(gap_to_top_quartile, unit),
                "Progress to top quartile": f"{progress_to_top_quartile:.0f}%",
                "Status": status,
                "Recommended AI improvement lever": get_recommendation(
                    metric=metric,
                    status=status,
                    industry=benchmark["industry"],
                ),
                "_progress_to_top_quartile": progress_to_top_quartile,
                "_gap_to_top_quartile": gap_to_top_quartile,
                "_status_color": STATUS_COLORS.get(status, "#6b7280"),
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
            worksheet.set_column(1, 7, 20)
            worksheet.set_column(8, 8, 72)

    return output.getvalue()


def style_status(value: str) -> str:
    color = STATUS_COLORS.get(value)
    if not color:
        return ""
    return f"background-color: {color}; color: white; font-weight: 700"


def render_status_cards(results_table: pd.DataFrame) -> None:
    status_counts = results_table["Status"].value_counts().to_dict()
    columns = st.columns(len(SCORE_ORDER))

    for column, status in zip(columns, SCORE_ORDER):
        count = status_counts.get(status, 0)
        color = STATUS_COLORS[status]
        column.markdown(
            f"""
            <div style="border-left: 6px solid {color}; padding: 0.75rem 0.9rem;
                        background: #f8fafc; border-radius: 0.4rem;">
                <div style="font-size: 0.82rem; color: #475569;">{status}</div>
                <div style="font-size: 1.7rem; font-weight: 700; color: #0f172a;">
                    {count}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_progress_chart(results_table: pd.DataFrame) -> alt.LayerChart:
    chart_data = results_table[
        ["Metric", "Status", "_progress_to_top_quartile", "_gap_to_top_quartile"]
    ].rename(
        columns={
            "_progress_to_top_quartile": "Progress to top quartile (%)",
            "_gap_to_top_quartile": "Gap to top quartile",
        }
    )

    bars = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadius=4)
        .encode(
            x=alt.X(
                "Progress to top quartile (%):Q",
                title="Progress to top quartile (%)",
            ),
            y=alt.Y("Metric:N", sort=None, title=None),
            color=alt.Color(
                "Status:N",
                scale=alt.Scale(
                    domain=list(STATUS_COLORS),
                    range=list(STATUS_COLORS.values()),
                ),
                legend=alt.Legend(title="Status"),
            ),
            tooltip=[
                "Metric:N",
                "Status:N",
                alt.Tooltip("Progress to top quartile (%):Q", format=".0f"),
                alt.Tooltip("Gap to top quartile:Q", format=".1f"),
            ],
        )
    )

    top_quartile_rule = (
        alt.Chart(pd.DataFrame({"Top quartile": [100]}))
        .mark_rule(color="#111827", strokeDash=[4, 4])
        .encode(x="Top quartile:Q")
    )

    return (bars + top_quartile_rule).properties(height=max(260, 34 * len(chart_data)))


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
display_table = results_table[DISPLAY_COLUMNS]

st.subheader("Performance overview")
render_status_cards(results_table)
st.altair_chart(build_progress_chart(results_table), width="stretch")

st.subheader("Detailed benchmark table")
styled_table = display_table.style.map(style_status, subset=["Status"])
st.dataframe(styled_table, width="stretch", hide_index=True)

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
    data=build_excel_export(display_table, industry, company_size),
    file_name=f"ai_benchmark_{file_safe_industry}_{file_safe_size}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
