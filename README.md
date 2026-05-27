# AI Benchmarking Tool

A Streamlit MVP for benchmarking company performance against sample market percentiles. Users select an industry, company size, and relevant metrics, then enter their own values to compare against the market median and top quartile.

## What The App Benchmarks

- Margin
- Productivity
- Growth
- Digital maturity

The first version uses sample benchmark data in `data/benchmark_data.csv`. No secrets, API keys, or paid services are required.

Metrics are data-driven by industry. For example, the Consulting industry includes:

- Utilization
- Revenue per employee
- EBITDA margin
- Growth
- Employee retention
- AI adoption
- Customer satisfaction
- Project delivery success

The results page includes status cards, a normalized progress chart, a color-coded benchmark table, and an Excel export of the benchmark comparison.

## Local Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
streamlit run app.py
```

4. Run tests:

```powershell
pytest
```

## Benchmark Data

The CSV file must include these columns:

- `industry`
- `company_size`
- `metric`
- `unit`
- `p25`
- `p50`
- `p75`

The scoring logic assumes higher values are better for all included MVP metrics:

- Below market: value is below `p25`
- Emerging: value is from `p25` up to below `p50`
- Competitive: value is from `p50` up to below `p75`
- Leading: value is at or above `p75`

To add or change industry-specific metrics, update `data/benchmark_data.csv` and add matching labels or recommendations in `app.py` and `src/recommendations.py` when needed.

## GitHub Setup

1. Create a new GitHub repository.
2. Push this project to the repository:

```powershell
git init
git add .
git commit -m "Create Streamlit AI benchmarking MVP"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

## Streamlit Community Cloud Deployment

1. Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Create a new app from your GitHub repository.
3. Set the main file path to `app.py`.
4. Deploy the app.

No secrets configuration is needed for this MVP.

## Project Structure

```text
app.py
data/benchmark_data.csv
src/scoring.py
src/recommendations.py
tests/test_scoring.py
tests/test_recommendations.py
requirements.txt
README.md
```
