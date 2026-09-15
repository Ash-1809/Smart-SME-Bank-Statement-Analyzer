def calculate_risk_score(
    summary: dict,
    stress_result: dict,
) -> dict:
    """
    Calculate an explainable financial risk score from 0 to 100.
    """

    risk_score = 0
    reasons = []

    net_cash_flow = float(summary.get("net_cash_flow", 0))
    total_income = float(summary.get("total_income", 0))
    total_expense = float(summary.get("total_expense", 0))
    minimum_balance = float(summary.get("minimum_balance", 0))

    # Check historical cash flow
    if net_cash_flow < 0:
        risk_score += 25
        reasons.append(
            "Historical expenses are greater than historical income."
        )

    # Check stress-simulation result
    stress_risk_level = stress_result.get("risk_level", "LOW")

    if stress_risk_level == "HIGH":
        risk_score += 40
        reasons.append(
            "The projected account balance becomes negative "
            "during the stress scenario."
        )

    elif stress_risk_level == "MEDIUM":
        risk_score += 25
        reasons.append(
            "The projected account balance falls below the "
            "minimum safe-balance limit."
        )

    # Calculate expense-to-income ratio
    if total_income > 0:
        expense_ratio = total_expense / total_income
    else:
        expense_ratio = 1.0
        reasons.append(
            "No historical business income was identified."
        )

    if expense_ratio >= 0.90:
        risk_score += 20
        reasons.append(
            "Expenses consume at least 90 percent of income."
        )

    elif expense_ratio >= 0.75:
        risk_score += 10
        reasons.append(
            "Expenses consume at least 75 percent of income."
        )

    # Check historical minimum balance
    if minimum_balance < 25000:
        risk_score += 15
        reasons.append(
            "The historical account balance crossed the "
            "safe cash limit."
        )

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        final_risk_level = "HIGH"
    elif risk_score >= 30:
        final_risk_level = "MEDIUM"
    else:
        final_risk_level = "LOW"

    if not reasons:
        reasons.append(
            "No major financial-stress indicators were identified."
        )

    return {
        "risk_score": risk_score,
        "risk_level": final_risk_level,
        "expense_ratio": round(expense_ratio, 4),
        "reasons": reasons,
    }