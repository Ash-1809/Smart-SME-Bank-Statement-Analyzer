from src.analyzer import (
    calculate_summary,
    categorize_statement,
    load_statement,
    validate_statement,
)
from src.explanation_service import generate_explanation
from src.stress_simulator import (
    create_baseline_forecast,
    run_stress_simulation,
)

from src.risk_scorer import calculate_risk_score
from src.voice_analyzer import analyze_voice_transcript


def main():
    dataframe = load_statement(
        "data/sample_bank_statement.csv"
    )

    validation = validate_statement(dataframe)

    dataframe = categorize_statement(dataframe)

    summary = calculate_summary(dataframe)

    baseline = create_baseline_forecast(
        dataframe=dataframe,
        summary=summary,
        forecast_days=60,
    )

    stress_result = run_stress_simulation(
        baseline=baseline,
        starting_balance=summary["closing_balance"],
        revenue_reduction=20,
        expense_increase=10,
        unexpected_expense=50000,
        unexpected_expense_day=15,
        safe_balance=25000,
    )

    risk_result = calculate_risk_score(
        summary=summary,
        stress_result=stress_result,
    )

    explanation = generate_explanation(
        risk_result=risk_result,
        stress_result=stress_result,
    )

    transcript = """
    Our sales have decreased during the last month.
    A customer delayed payment for an important invoice.
    We also had an unexpected machine repair.
    """

    voice_result = analyze_voice_transcript(transcript)

    print("\nVALIDATION")
    print(validation)

    print("\nFINANCIAL SUMMARY")
    print(summary)

    print("\nSTRESS RESULT")
    print({
        "risk_level": stress_result["risk_level"],
        "cash_runway_days":
            stress_result["cash_runway_days"],
        "minimum_stressed_balance":
            stress_result["minimum_stressed_balance"],
        "first_low_balance_date":
            stress_result["first_low_balance_date"],
    })

    print("\nRISK RESULT")
    print(risk_result)

    print("\nLANGCHAIN EXPLANATION")
    print(explanation)

    print("\nVOICE ANALYSIS")
    print(voice_result)


if __name__ == "__main__":
    main()