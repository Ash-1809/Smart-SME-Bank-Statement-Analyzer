from typing import Any

import pandas as pd
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from src.analyzer import (
    calculate_summary,
    categorize_statement,
    load_statement,
    validate_statement,
)
from src.explanation_service import generate_explanation
from src.risk_scorer import calculate_risk_score
from src.stress_simulator import (
    create_baseline_forecast,
    run_stress_simulation,
)
from src.voice_analyzer import analyze_voice_transcript


class AnalysisState(TypedDict, total=False):
    """
    Shared state passed between all LangGraph nodes.
    """

    file_path: str

    forecast_days: int
    revenue_reduction: float
    expense_increase: float
    unexpected_expense: float
    unexpected_expense_day: int
    safe_balance: float

    voice_transcript: str

    dataframe: Any
    validation_result: dict
    financial_summary: dict
    baseline_forecast: Any
    stress_result: dict
    risk_result: dict
    explanation: str
    voice_result: dict

    workflow_status: str
    error_message: str


def load_statement_node(state: AnalysisState) -> dict:
    """
    Load the uploaded bank statement.
    """

    try:
        dataframe = load_statement(state["file_path"])

        return {
            "dataframe": dataframe,
            "workflow_status": "STATEMENT_LOADED",
            "error_message": "",
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Statement loading failed: {str(error)}"
            ),
        }


def validate_statement_node(state: AnalysisState) -> dict:
    """
    Validate the loaded bank statement.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    dataframe = state.get("dataframe")

    if dataframe is None:
        return {
            "workflow_status": "FAILED",
            "error_message": "No dataframe was available for validation.",
        }

    try:
        validation_result = validate_statement(dataframe)

        status = (
            "STATEMENT_VALIDATED"
            if validation_result["is_valid"]
            else "VALIDATION_WARNING"
        )

        return {
            "validation_result": validation_result,
            "workflow_status": status,
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Statement validation failed: {str(error)}"
            ),
        }


def categorize_transactions_node(
    state: AnalysisState,
) -> dict:
    """
    Categorize all bank transactions.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    try:
        categorized_dataframe = categorize_statement(
            state["dataframe"]
        )

        return {
            "dataframe": categorized_dataframe,
            "workflow_status": "TRANSACTIONS_CATEGORIZED",
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Transaction categorization failed: {str(error)}"
            ),
        }


def calculate_summary_node(state: AnalysisState) -> dict:
    """
    Calculate income, expense, balance and other indicators.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    try:
        summary = calculate_summary(state["dataframe"])

        return {
            "financial_summary": summary,
            "workflow_status": "SUMMARY_CALCULATED",
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Financial summary failed: {str(error)}"
            ),
        }


def create_forecast_node(state: AnalysisState) -> dict:
    """
    Create the baseline cash-flow forecast.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    try:
        forecast_days = int(state.get("forecast_days", 60))

        baseline = create_baseline_forecast(
            dataframe=state["dataframe"],
            summary=state["financial_summary"],
            forecast_days=forecast_days,
        )

        return {
            "baseline_forecast": baseline,
            "workflow_status": "FORECAST_CREATED",
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Cash-flow forecast failed: {str(error)}"
            ),
        }


def stress_simulation_node(state: AnalysisState) -> dict:
    """
    Apply selected financial stress conditions.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    try:
        summary = state["financial_summary"]

        stress_result = run_stress_simulation(
            baseline=state["baseline_forecast"],
            starting_balance=summary["closing_balance"],
            revenue_reduction=float(
                state.get("revenue_reduction", 20)
            ),
            expense_increase=float(
                state.get("expense_increase", 10)
            ),
            unexpected_expense=float(
                state.get("unexpected_expense", 50000)
            ),
            unexpected_expense_day=int(
                state.get("unexpected_expense_day", 15)
            ),
            safe_balance=float(
                state.get("safe_balance", 25000)
            ),
        )

        return {
            "stress_result": stress_result,
            "workflow_status": "STRESS_SIMULATION_COMPLETED",
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Stress simulation failed: {str(error)}"
            ),
        }


def risk_scoring_node(state: AnalysisState) -> dict:
    """
    Calculate the final explainable financial-risk score.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    try:
        risk_result = calculate_risk_score(
            summary=state["financial_summary"],
            stress_result=state["stress_result"],
        )

        return {
            "risk_result": risk_result,
            "workflow_status": "RISK_SCORE_CALCULATED",
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Risk scoring failed: {str(error)}"
            ),
        }


def explanation_node(state: AnalysisState) -> dict:
    """
    Generate the LangChain-formatted explanation.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    try:
        explanation = generate_explanation(
            risk_result=state["risk_result"],
            stress_result=state["stress_result"],
        )

        return {
            "explanation": explanation,
            "workflow_status": "EXPLANATION_GENERATED",
        }

    except Exception as error:
        return {
            "workflow_status": "FAILED",
            "error_message": (
                f"Explanation generation failed: {str(error)}"
            ),
        }


def voice_analysis_node(state: AnalysisState) -> dict:
    """
    Analyze an optional SME customer-call transcript.
    """

    if state.get("workflow_status") == "FAILED":
        return {}

    transcript = state.get("voice_transcript", "").strip()

    if not transcript:
        return {
            "voice_result": {
                "status": "NO_TRANSCRIPT_PROVIDED",
                "signals": [],
                "signal_count": 0,
            },
            "workflow_status": "WORKFLOW_COMPLETED",
        }

    try:
        voice_result = analyze_voice_transcript(transcript)

        return {
            "voice_result": voice_result,
            "workflow_status": "WORKFLOW_COMPLETED",
        }

    except Exception as error:
        return {
            "voice_result": {
                "status": "VOICE_ANALYSIS_FAILED",
                "signals": [],
                "signal_count": 0,
            },
            "workflow_status": "WORKFLOW_COMPLETED",
            "error_message": (
                f"Voice analysis failed: {str(error)}"
            ),
        }


def build_analysis_graph():
    """
    Create and compile the complete LangGraph workflow.
    """

    graph_builder = StateGraph(AnalysisState)

    graph_builder.add_node(
        "load_statement",
        load_statement_node,
    )

    graph_builder.add_node(
        "validate_statement",
        validate_statement_node,
    )

    graph_builder.add_node(
        "categorize_transactions",
        categorize_transactions_node,
    )

    graph_builder.add_node(
        "calculate_summary",
        calculate_summary_node,
    )

    graph_builder.add_node(
        "create_forecast",
        create_forecast_node,
    )

    graph_builder.add_node(
        "stress_simulation",
        stress_simulation_node,
    )

    graph_builder.add_node(
        "risk_scoring",
        risk_scoring_node,
    )

    graph_builder.add_node(
        "generate_explanation",
        explanation_node,
    )

    graph_builder.add_node(
        "voice_analysis",
        voice_analysis_node,
    )

    graph_builder.add_edge(
        START,
        "load_statement",
    )

    graph_builder.add_edge(
        "load_statement",
        "validate_statement",
    )

    graph_builder.add_edge(
        "validate_statement",
        "categorize_transactions",
    )

    graph_builder.add_edge(
        "categorize_transactions",
        "calculate_summary",
    )

    graph_builder.add_edge(
        "calculate_summary",
        "create_forecast",
    )

    graph_builder.add_edge(
        "create_forecast",
        "stress_simulation",
    )

    graph_builder.add_edge(
        "stress_simulation",
        "risk_scoring",
    )

    graph_builder.add_edge(
        "risk_scoring",
        "generate_explanation",
    )

    graph_builder.add_edge(
        "generate_explanation",
        "voice_analysis",
    )

    graph_builder.add_edge(
        "voice_analysis",
        END,
    )

    return graph_builder.compile()


analysis_graph = build_analysis_graph()