from langchain_core.prompts import PromptTemplate


EXPLANATION_TEMPLATE = """
SME Financial Stress Analysis

Overall risk level: {risk_level}
Risk score: {risk_score}/100
Cash runway: {cash_runway_days} days
Minimum stressed balance: INR {minimum_balance:,.2f}
Final stressed balance: INR {final_balance:,.2f}

Scenario applied:
- Revenue reduction: {revenue_reduction}%
- Expense increase: {expense_increase}%
- Unexpected expense: INR {unexpected_expense:,.2f}

Risk reasons:
{risk_reasons}

Recommended actions:
{recommendations}

Important:
This result is a decision-support assessment.
Final lending decisions must be reviewed by an authorized bank officer.
"""


def generate_explanation(
    risk_result: dict,
    stress_result: dict,
) -> str:
    """Generate a consistent explanation using LangChain."""

    if risk_result["risk_level"] == "HIGH":
        recommendations = [
            "Review upcoming supplier and EMI obligations.",
            "Contact customers associated with delayed payments.",
            "Maintain a higher operational cash reserve.",
            "Send the account for manual relationship-manager review.",
        ]
    elif risk_result["risk_level"] == "MEDIUM":
        recommendations = [
            "Monitor the balance every week.",
            "Review non-essential operational expenses.",
            "Follow up on pending customer payments.",
        ]
    else:
        recommendations = [
            "Continue monitoring recurring obligations.",
            "Maintain the current safe cash buffer.",
        ]

    prompt = PromptTemplate.from_template(
        EXPLANATION_TEMPLATE
    )

    return prompt.format(
        risk_level=risk_result["risk_level"],
        risk_score=risk_result["risk_score"],
        cash_runway_days=stress_result["cash_runway_days"],
        minimum_balance=stress_result[
            "minimum_stressed_balance"
        ],
        final_balance=stress_result[
            "final_stressed_balance"
        ],
        revenue_reduction=stress_result[
            "scenario"
        ]["revenue_reduction"],
        expense_increase=stress_result[
            "scenario"
        ]["expense_increase"],
        unexpected_expense=stress_result[
            "scenario"
        ]["unexpected_expense"],
        risk_reasons="\n".join(
            f"- {reason}"
            for reason in risk_result["reasons"]
        ),
        recommendations="\n".join(
            f"- {recommendation}"
            for recommendation in recommendations
        ),
    )