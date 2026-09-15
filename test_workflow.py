from workflow.analysis_graph import analysis_graph


def main():
    initial_state = {
        "file_path": "data/sample_bank_statement.csv",
        "forecast_days": 60,
        "revenue_reduction": 20,
        "expense_increase": 10,
        "unexpected_expense": 50000,
        "unexpected_expense_day": 15,
        "safe_balance": 25000,
        "voice_transcript": """
        Our sales have decreased during the last month.
        A customer delayed payment for an important invoice.
        We also had an unexpected machine repair.
        """,
        "workflow_status": "STARTED",
        "error_message": "",
    }

    final_state = analysis_graph.invoke(initial_state)

    print("\nLANGGRAPH WORKFLOW RESULT")
    print("=" * 50)

    print(
        "Workflow status:",
        final_state.get("workflow_status"),
    )

    error_message = final_state.get("error_message")

    if error_message:
        print("Error:", error_message)

    print("\nVALIDATION RESULT")
    print(final_state.get("validation_result"))

    print("\nFINANCIAL SUMMARY")
    print(final_state.get("financial_summary"))

    stress_result = final_state.get("stress_result", {})

    print("\nSTRESS SIMULATION")
    print({
        "risk_level": stress_result.get("risk_level"),
        "cash_runway_days":
            stress_result.get("cash_runway_days"),
        "minimum_stressed_balance":
            stress_result.get("minimum_stressed_balance"),
        "first_low_balance_date":
            stress_result.get("first_low_balance_date"),
        "first_negative_balance_date":
            stress_result.get("first_negative_balance_date"),
    })

    print("\nRISK SCORE")
    print(final_state.get("risk_result"))

    print("\nLANGCHAIN EXPLANATION")
    print(final_state.get("explanation"))

    print("\nVOICE SIGNAL RESULT")
    print(final_state.get("voice_result"))


if __name__ == "__main__":
    main()