import re

import pandas as pd


REQUIRED_COLUMNS = {
    "transaction_id",
    "date",
    "description",
    "debit",
    "credit",
    "balance",
}


CATEGORY_RULES = {
    "Revenue": [
        "customer payment",
        "sales",
        "receipt",
        "collection",
    ],
    "Rent": [
        "rent",
        "lease",
    ],
    "Salary": [
        "salary",
        "payroll",
        "employee",
    ],
    "Supplier Payment": [
        "supplier",
        "vendor",
        "wholesale",
        "packaging",
    ],
    "Loan EMI": [
        "emi",
        "loan repayment",
        "loan installment",
    ],
    "Utilities": [
        "electricity",
        "internet",
        "phone bill",
        "water bill",
    ],
    "Tax": [
        "gst",
        "tax",
        "tds",
    ],
    "Marketing": [
        "marketing",
        "advertisement",
        "promotion",
    ],
    "Insurance": [
        "insurance",
        "premium",
    ],
    "Cash Withdrawal": [
        "cash withdrawal",
        "atm",
    ],
    "Emergency Expense": [
        "repair",
        "emergency",
        "replacement",
    ],
}


def load_statement(file_source) -> pd.DataFrame:
    """Load and standardize a CSV bank statement."""

    dataframe = pd.read_csv(file_source)

    dataframe.columns = [
        column.strip().lower().replace(" ", "_")
        for column in dataframe.columns
    ]

    missing = REQUIRED_COLUMNS.difference(dataframe.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        errors="coerce"
    )

    for column in ["debit", "credit", "balance"]:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce"
        ).fillna(0)

    dataframe["description"] = (
        dataframe["description"]
        .fillna("Unknown Transaction")
        .astype(str)
        .str.strip()
    )

    dataframe = dataframe.drop_duplicates(
        subset=["date", "description", "debit", "credit"]
    )

    return dataframe.sort_values("date").reset_index(drop=True)


def validate_statement(dataframe: pd.DataFrame) -> dict:
    """Validate basic statement quality."""

    issues = []

    invalid_dates = int(dataframe["date"].isna().sum())
    negative_debits = int((dataframe["debit"] < 0).sum())
    negative_credits = int((dataframe["credit"] < 0).sum())

    both_values = int(
        (
            (dataframe["debit"] > 0) &
            (dataframe["credit"] > 0)
        ).sum()
    )

    if invalid_dates:
        issues.append(f"{invalid_dates} invalid dates found.")

    if negative_debits:
        issues.append(
            f"{negative_debits} negative debit amounts found."
        )

    if negative_credits:
        issues.append(
            f"{negative_credits} negative credit amounts found."
        )

    if both_values:
        issues.append(
            f"{both_values} rows contain both debit and credit."
        )

    quality_score = max(
        0,
        100
        - invalid_dates * 10
        - negative_debits * 5
        - negative_credits * 5
        - both_values * 5
    )

    return {
        "is_valid": len(issues) == 0,
        "quality_score": quality_score,
        "issues": issues,
    }


def clean_description(description: str) -> str:
    description = description.lower()
    description = re.sub(r"\d+", " ", description)
    description = re.sub(r"[^a-z\s]", " ", description)
    description = re.sub(r"\s+", " ", description)

    return description.strip()


def categorize_transaction(row: pd.Series) -> tuple:
    """Return category, confidence and explanation."""

    description = clean_description(row["description"])

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in description:
                return (
                    category,
                    0.95,
                    f"Matched business keyword: {keyword}",
                )

    if row["credit"] > 0:
        return (
            "Other Income",
            0.60,
            "Unmatched credit transaction",
        )

    return (
        "Other Expense",
        0.50,
        "Unmatched debit transaction",
    )


def categorize_statement(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """Categorize all transactions."""

    result = dataframe.copy()

    predictions = result.apply(
        categorize_transaction,
        axis=1
    )

    result["category"] = [
        prediction[0] for prediction in predictions
    ]

    result["confidence"] = [
        prediction[1] for prediction in predictions
    ]

    result["category_reason"] = [
        prediction[2] for prediction in predictions
    ]

    return result


def calculate_summary(dataframe: pd.DataFrame) -> dict:
    """Calculate the main financial indicators."""

    total_income = float(dataframe["credit"].sum())
    total_expense = float(dataframe["debit"].sum())
    net_cash_flow = total_income - total_expense
    closing_balance = float(dataframe.iloc[-1]["balance"])
    minimum_balance = float(dataframe["balance"].min())
    average_balance = float(dataframe["balance"].mean())

    category_expenses = (
        dataframe[dataframe["debit"] > 0]
        .groupby("category")["debit"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    recurring_categories = [
        "Rent",
        "Salary",
        "Loan EMI",
        "Utilities",
        "Insurance",
    ]

    recurring_expenses = float(
        dataframe[
            dataframe["category"].isin(recurring_categories)
        ]["debit"].sum()
    )

    period_days = max(
        (
            dataframe["date"].max() -
            dataframe["date"].min()
        ).days,
        1
    )

    average_daily_income = total_income / period_days
    average_daily_expense = total_expense / period_days

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_cash_flow": net_cash_flow,
        "closing_balance": closing_balance,
        "minimum_balance": minimum_balance,
        "average_balance": average_balance,
        "recurring_expenses": recurring_expenses,
        "average_daily_income": average_daily_income,
        "average_daily_expense": average_daily_expense,
        "category_expenses": category_expenses,
        "statement_days": period_days,
    }
    