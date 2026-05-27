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

INDUSTRY_RECOMMENDATIONS = {
    "Consulting": {
        "utilization": {
            "Below market": "Use AI-based resource planning to identify bench time, staffing mismatches, and faster redeployment opportunities.",
            "Emerging": "Introduce AI-supported capacity forecasting and weekly utilization alerts for team leads.",
            "Competitive": "Connect pipeline, staffing, and delivery data so AI can recommend earlier allocation decisions.",
            "Leading": "Use predictive staffing models to protect utilization while preserving learning time and delivery quality.",
        },
        "revenue_per_employee": {
            "Below market": "Use AI copilots for proposal writing, research, analysis, and delivery documentation to lift consultant leverage.",
            "Emerging": "Standardize reusable AI-assisted assets for sales decks, analysis templates, and project reporting.",
            "Competitive": "Scale AI-enabled delivery accelerators across practices to improve leverage without reducing quality.",
            "Leading": "Package high-value AI accelerators into repeatable offerings that increase revenue per consultant.",
        },
        "ebitda_margin": {
            "Below market": "Use AI to review project profitability, scope drift, subcontractor spend, and pricing leakage.",
            "Emerging": "Add AI-supported margin reviews before proposals and at key project checkpoints.",
            "Competitive": "Use predictive project margin models to flag delivery risk before it erodes profitability.",
            "Leading": "Protect margin with AI scenario planning across pricing, staffing mix, and delivery model choices.",
        },
        "growth": {
            "Below market": "Use AI for account whitespace analysis, lead prioritization, and targeted thought-leadership campaigns.",
            "Emerging": "Add AI-supported next-best-action recommendations for account teams and bid managers.",
            "Competitive": "Scale AI-assisted sales intelligence across sectors, offerings, and partner channels.",
            "Leading": "Use predictive demand signals to shape new offerings and enter high-potential client segments earlier.",
        },
        "employee_retention": {
            "Below market": "Use AI-enabled people analytics to identify burnout, staffing pressure, and skills mismatch patterns.",
            "Emerging": "Introduce AI-supported career pathing, skills matching, and staffing preference capture.",
            "Competitive": "Use AI to balance utilization, development goals, and project fit across staffing decisions.",
            "Leading": "Apply predictive retention insights to personalize growth, learning, and leadership interventions.",
        },
        "ai_adoption": {
            "Below market": "Start with a practical AI enablement program for consultants, including approved tools and clear use cases.",
            "Emerging": "Create role-based AI playbooks for sales, delivery, research, project management, and knowledge sharing.",
            "Competitive": "Measure adoption, quality, and time saved across teams, then scale the highest-value use cases.",
            "Leading": "Industrialize AI adoption through reusable prompt libraries, governed accelerators, and internal communities of practice.",
        },
        "customer_satisfaction": {
            "Below market": "Use AI to summarize feedback, detect delivery risks, and trigger faster corrective actions with project sponsors.",
            "Emerging": "Add AI-supported sentiment analysis across surveys, meeting notes, and project retrospectives.",
            "Competitive": "Use AI to identify satisfaction drivers and recommend targeted actions by account and project type.",
            "Leading": "Turn AI-driven satisfaction insights into proactive client success plays and differentiated advisory moments.",
        },
        "project_delivery_success": {
            "Below market": "Use AI project controls to flag schedule risk, unclear scope, and unresolved dependencies earlier.",
            "Emerging": "Introduce AI-assisted status reporting, risk registers, and delivery quality checks.",
            "Competitive": "Connect delivery data so AI can recommend interventions before milestones slip.",
            "Leading": "Use predictive delivery assurance across the portfolio to improve consistency and reuse best practices.",
        },
    }
}


def get_recommendation(metric: str, status: str, industry: str | None = None) -> str:
    if industry:
        industry_recommendations = INDUSTRY_RECOMMENDATIONS.get(industry, {})
        recommendation = industry_recommendations.get(metric, {}).get(status)
        if recommendation:
            return recommendation

    return RECOMMENDATIONS.get(metric, {}).get(status, DEFAULT_RECOMMENDATION)


def get_score_explanation(status: str) -> str:
    return SCORE_EXPLANATIONS.get(status, "No explanation is available for this score.")
