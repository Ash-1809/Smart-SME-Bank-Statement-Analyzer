from datetime import timedelta

import pandas as pd


def create_baseline_forecast(
    dataframe: pd.DataFrame,
    summary: dict,
    forecast_days: int = 60,
) -> pd.DataFrame:
    """
    Create a daily cash-flow forecast using historical
    average income and expenditure.
    """

    current_balance = float(summary["closing_balance"])
    daily_income = float(summary["average_daily_income"])
    daily_expense = float(summary["average_daily_expense"])

    last_date = pd.to_datetime(dataframe["date"]).max()

    records = []

    for day in range(1, forecast_days + 1):
        forecast_date = last_date + timedelta(days=day)

        current_balance += daily_income - daily_expense

        records.append(
            {
                "day": day,
                "date": forecast_date,
                "expected_income": daily_income,
                "expected_expense": daily_expense,
                "baseline_balance": current_balance,
            }
        )

    return pd.DataFrame(records)


def run_stress_simulation(
    baseline: pd.DataFrame,
    starting_balance: float,
    revenue_reduction: float = 20,
    expense_increase: float = 10,
    unexpected_expense: float = 50000,
    unexpected_expense_day: int = 15,
    safe_balance: float = 25000,
) -> dict:
    """
    Apply financial shocks to the baseline forecast.
    """

    if baseline.empty:
        raise ValueError("The baseline forecast is empty.")

    result = baseline.copy()

    revenue_multiplier = 1 - (revenue_reduction / 100)
    expense_multiplier = 1 + (expense_increase / 100)

    result["stressed_income"] = (
        result["expected_income"] * revenue_multiplier
    )

    result["stressed_expense"] = (
        result["expected_expense"] * expense_multiplier
    )

    stressed_balance = float(starting_balance)
    stressed_balances = []
    actual_stressed_expenses = []

    for _, row in result.iterrows():
        daily_expense = float(row["stressed_expense"])

        if int(row["day"]) == int(unexpected_expense_day):
            daily_expense += float(unexpected_expense)

        stressed_balance += (
            float(row["stressed_income"]) - daily_expense
        )

        actual_stressed_expenses.append(daily_expense)
        stressed_balances.append(stressed_balance)

    result["actual_stressed_expense"] = actual_stressed_expenses
    result["stressed_balance"] = stressed_balances

    low_balance_rows = result[
        result["stressed_balance"] < safe_balance
    ]

    negative_balance_rows = result[
        result["stressed_balance"] < 0
    ]

    first_low_balance_date = None
    first_negative_balance_date = None

    if not low_balance_rows.empty:
        first_low_balance_date = low_balance_rows.iloc[0]["date"]

    if not negative_balance_rows.empty:
        first_negative_balance_date = (
            negative_balance_rows.iloc[0]["date"]
        )

    if first_negative_balance_date is not None:
        risk_level = "HIGH"
        cash_runway_days = int(
            negative_balance_rows.iloc[0]["day"]
        )

    elif first_low_balance_date is not None:
        risk_level = "MEDIUM"
        cash_runway_days = int(
            low_balance_rows.iloc[0]["day"]
        )

    else:
        risk_level = "LOW"
        cash_runway_days = int(len(result))

    return {
        "forecast": result,
        "risk_level": risk_level,
        "cash_runway_days": cash_runway_days,
        "first_low_balance_date": first_low_balance_date,
        "first_negative_balance_date": first_negative_balance_date,
        "minimum_stressed_balance": float(
            result["stressed_balance"].min()
        ),
        "final_stressed_balance": float(
            result.iloc[-1]["stressed_balance"]
        ),
        "scenario": {
            "revenue_reduction": float(revenue_reduction),
            "expense_increase": float(expense_increase),
            "unexpected_expense": float(unexpected_expense),
            "unexpected_expense_day": int(
                unexpected_expense_day
            ),
            "safe_balance": float(safe_balance),
        },
    }