DEFAULT_RECOMMENDATION = "Prioritize one focused AI pilot with clear ownership, baseline metrics, and a 90-day impact target."

SCORE_EXPLANATIONS = {
    "Below market": "Below the 25th percentile. This area is likely limiting performance.",
    "Emerging": "Between the 25th percentile and market median. There is visible room to improve.",
    "Competitive": "Between market median and the 75th percentile. Performance is solid, with room to scale.",
    "Leading": "At or above the 75th percentile. Protect the advantage and look for selective next bets.",
}

RECOMMENDATIONS = {
    "margin": {
        "Below market": "Use AI-assisted spend analytics, pricing reviews, and process automation to target margin leakage.",
        "Emerging": "Automate recurring back-office tasks and use AI to identify pricing and mix opportunities.",
        "Competitive": "Scale AI forecasting and profitability analysis across products, customers, and channels.",
        "Leading": "Use AI scenario planning to protect margin while funding selective growth bets.",
    },
    "productivity": {
        "Below market": "Start with workflow automation for repetitive manual tasks and AI copilots for high-volume roles.",
        "Emerging": "Standardize AI assistants for sales, service, finance, and operations teams.",
        "Competitive": "Connect AI tools to core systems so teams can automate handoffs and reporting.",
        "Leading": "Move toward agentic workflows for complex, multi-step processes with human review.",
    },
    "growth": {
        "Below market": "Use AI for customer segmentation, lead scoring, and campaign personalization to improve pipeline quality.",
        "Emerging": "Add AI-supported sales prioritization and next-best-action recommendations.",
        "Competitive": "Scale AI experimentation across acquisition, retention, and expansion motions.",
        "Leading": "Use predictive growth models to identify new markets, products, and pricing moves.",
    },
    "digital_maturity": {
        "Below market": "Build the foundation: clean data ownership, basic dashboards, and a small set of practical AI use cases.",
        "Emerging": "Create reusable data assets and lightweight governance for AI pilots.",
        "Competitive": "Integrate AI into standard workflows and track adoption, quality, and value creation.",
        "Leading": "Industrialize AI delivery with portfolio governance, model monitoring, and reusable platforms.",
    },
}


def get_recommendation(metric: str, status: str) -> str:
    return RECOMMENDATIONS.get(metric, {}).get(status, DEFAULT_RECOMMENDATION)


def get_score_explanation(status: str) -> str:
    return SCORE_EXPLANATIONS.get(status, "No explanation is available for this score.")
