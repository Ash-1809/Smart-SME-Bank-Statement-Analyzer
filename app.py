from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from workflow.analysis_graph import analysis_graph


st.set_page_config(
    page_title="Smart SME Analyzer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        .stApp { background-color: #f4f7fb; }
        .main .block-container {
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1450px;
        }
        .main-header {
            background: linear-gradient(120deg, #071952 0%, #0b4f9c 55%, #088395 100%);
            padding: 28px 32px;
            border-radius: 18px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(7, 25, 82, 0.20);
        }
        .main-header h1 { color: white; margin: 0; font-size: 34px; }
        .main-header p { color: #e7f5ff; margin: 8px 0 0 0; font-size: 16px; }
        .section-header {
            font-size: 22px;
            font-weight: 700;
            color: #071952;
            border-left: 5px solid #088395;
            padding-left: 12px;
            margin: 15px 0;
        }
        .info-box {
            background: white;
            border: 1px solid #dbe4f0;
            padding: 18px;
            border-radius: 12px;
            color: #263238;
            margin-bottom: 12px;
        }
        .high-risk {
            background-color: #fff1f1;
            border-left: 6px solid #d32f2f;
            padding: 18px;
            border-radius: 12px;
            color: #8b0000;
            margin: 10px 0 15px 0;
        }
        .medium-risk {
            background-color: #fff8e1;
            border-left: 6px solid #f9a825;
            padding: 18px;
            border-radius: 12px;
            color: #704a00;
            margin: 10px 0 15px 0;
        }
        .low-risk {
            background-color: #edf8f0;
            border-left: 6px solid #2e7d32;
            padding: 18px;
            border-radius: 12px;
            color: #145a1e;
            margin: 10px 0 15px 0;
        }
        div[data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #dfe7f1;
            padding: 15px;
            border-radius: 14px;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
        }
        .footer {
            text-align: center;
            color: #607d8b;
            padding-top: 25px;
            font-size: 13px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_inr(value) -> str:
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def format_date(value) -> str:
    if value is None:
        return "Not expected"
    try:
        return pd.to_datetime(value).strftime("%d %b %Y")
    except (TypeError, ValueError):
        return str(value)


def get_risk_class(risk_level: str) -> str:
    return {
        "HIGH": "high-risk",
        "MEDIUM": "medium-risk",
        "LOW": "low-risk",
    }.get(risk_level, "info-box")


def save_uploaded_file(uploaded_file) -> str:
    data_directory = Path("data")
    data_directory.mkdir(exist_ok=True)
    uploaded_path = data_directory / "uploaded_statement.csv"
    uploaded_path.write_bytes(uploaded_file.getbuffer())
    return str(uploaded_path)


def run_analysis(
    file_path: str,
    forecast_days: int,
    revenue_reduction: float,
    expense_increase: float,
    unexpected_expense: float,
    unexpected_expense_day: int,
    safe_balance: float,
    voice_transcript: str,
) -> dict:
    initial_state = {
        "file_path": file_path,
        "forecast_days": forecast_days,
        "revenue_reduction": revenue_reduction,
        "expense_increase": expense_increase,
        "unexpected_expense": unexpected_expense,
        "unexpected_expense_day": unexpected_expense_day,
        "safe_balance": safe_balance,
        "voice_transcript": voice_transcript,
        "workflow_status": "STARTED",
        "error_message": "",
    }
    return analysis_graph.invoke(initial_state)


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_completed" not in st.session_state:
    st.session_state.analysis_completed = False


st.markdown(
    """
    <div class="main-header">
        <h1>🏦 Smart SME Bank Statement Analyzer</h1>
        <p>Transaction categorization, cash-flow forecasting, stress simulation and voice-risk intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.title("⚙️ Analysis Controls")
    st.caption("Choose a statement and configure the financial stress scenario.")

    uploaded_file = st.file_uploader(
        "Upload bank statement",
        type=["csv"],
        help="Required columns: transaction_id, date, description, debit, credit and balance.",
    )
    use_sample_data = st.checkbox(
        "Use sample bank statement",
        value=uploaded_file is None,
    )

    st.divider()
    st.subheader("📅 Forecast Settings")
    forecast_days = st.slider("Forecast period", 30, 90, 60, 15)

    st.divider()
    st.subheader("⚠️ Stress Scenario")
    revenue_reduction = st.slider("Revenue reduction (%)", 0, 60, 20, 5)
    expense_increase = st.slider("Expense increase (%)", 0, 50, 10, 5)
    unexpected_expense = st.number_input(
        "Unexpected expense (₹)",
        min_value=0.0,
        max_value=1000000.0,
        value=50000.0,
        step=5000.0,
    )
    unexpected_expense_day = st.slider(
        "Unexpected expense occurs on day",
        min_value=1,
        max_value=forecast_days,
        value=min(15, forecast_days),
    )
    safe_balance = st.number_input(
        "Minimum safe balance (₹)",
        min_value=0.0,
        max_value=1000000.0,
        value=25000.0,
        step=5000.0,
    )

    st.divider()
    st.subheader("🎙️ Voice Intelligence")
    voice_transcript = st.text_area(
        "SME customer-call transcript",
        value=(
            "Our sales have decreased during the last month. "
            "A customer delayed payment for an important invoice. "
            "We also had an unexpected machine repair."
        ),
        height=150,
    )

    analyze_button = st.button(
        "🚀 Run Complete Analysis",
        type="primary",
        use_container_width=True,
    )
    reset_button = st.button("Reset Dashboard", use_container_width=True)


if reset_button:
    st.session_state.analysis_result = None
    st.session_state.analysis_completed = False
    st.rerun()


if analyze_button:
    try:
        if uploaded_file is not None:
            selected_file_path = save_uploaded_file(uploaded_file)
        elif use_sample_data:
            selected_file_path = "data/sample_bank_statement.csv"
            if not Path(selected_file_path).exists():
                st.error("Sample file not found at data/sample_bank_statement.csv.")
                st.stop()
        else:
            st.warning("Upload a CSV file or select the sample bank statement.")
            st.stop()

        with st.spinner("LangGraph is processing the bank statement..."):
            final_state = run_analysis(
                file_path=selected_file_path,
                forecast_days=forecast_days,
                revenue_reduction=revenue_reduction,
                expense_increase=expense_increase,
                unexpected_expense=unexpected_expense,
                unexpected_expense_day=unexpected_expense_day,
                safe_balance=safe_balance,
                voice_transcript=voice_transcript,
            )

        if final_state.get("workflow_status") == "FAILED":
            st.session_state.analysis_completed = False
            st.error(final_state.get("error_message", "The workflow failed."))
        else:
            st.session_state.analysis_result = final_state
            st.session_state.analysis_completed = True
            st.success("Bank statement analysis completed successfully.")
    except Exception as error:
        st.session_state.analysis_completed = False
        st.error(f"Dashboard analysis failed: {error}")


if not st.session_state.analysis_completed:
    st.markdown('<div class="section-header">Project Overview</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="info-box">
                <h3>📊 Statement Intelligence</h3>
                <p>Categorizes SME transactions and calculates income, expenses, balances and recurring obligations.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="info-box">
                <h3>💡 Unique Feature</h3>
                <p>The stress simulator predicts how reduced revenue, higher expenses and an unexpected cost affect future cash flow.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.info("Configure the sidebar and click Run Complete Analysis.")
    st.stop()


result = st.session_state.analysis_result or {}
dataframe = result.get("dataframe")
validation = result.get("validation_result", {})
summary = result.get("financial_summary", {})
stress_result = result.get("stress_result", {})
risk_result = result.get("risk_result", {})
explanation = result.get("explanation", "")
voice_result = result.get("voice_result", {})
stress_forecast = stress_result.get("forecast")
workflow_status = result.get("workflow_status", "UNKNOWN")


st.markdown('<div class="section-header">Workflow Execution</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("LangGraph Status", workflow_status.replace("_", " ").title())
with col2:
    st.metric("Data Quality Score", f"{validation.get('quality_score', 0)}/100")
with col3:
    count = len(dataframe) if isinstance(dataframe, pd.DataFrame) else 0
    st.metric("Transactions Processed", f"{count:,}")

if validation.get("issues"):
    with st.expander("View validation warnings"):
        for issue in validation["issues"]:
            st.warning(issue)
else:
    st.success("Statement validation completed without major errors.")


tabs = st.tabs(
    [
        "📌 Executive Summary",
        "💳 Transactions",
        "📈 Cash-Flow Forecast",
        "⚠️ Stress Simulator",
        "🎙️ Voice Intelligence",
        "🧠 Technical Details",
    ]
)


with tabs[0]:
    st.markdown('<div class="section-header">Financial Overview</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Income", format_inr(summary.get("total_income", 0)))
    with m2:
        st.metric("Total Expenses", format_inr(summary.get("total_expense", 0)))
    with m3:
        net_cash_flow = float(summary.get("net_cash_flow", 0))
        st.metric(
            "Net Cash Flow",
            format_inr(net_cash_flow),
            delta="Positive" if net_cash_flow >= 0 else "Negative",
            delta_color="normal" if net_cash_flow >= 0 else "inverse",
        )
    with m4:
        st.metric("Closing Balance", format_inr(summary.get("closing_balance", 0)))

    m5, m6, m7, m8 = st.columns(4)
    with m5:
        st.metric("Average Balance", format_inr(summary.get("average_balance", 0)))
    with m6:
        st.metric("Minimum Balance", format_inr(summary.get("minimum_balance", 0)))
    with m7:
        st.metric("Recurring Expenses", format_inr(summary.get("recurring_expenses", 0)))
    with m8:
        st.metric("Statement Period", f"{summary.get('statement_days', 0)} days")

    st.markdown('<div class="section-header">Overall Risk Result</div>', unsafe_allow_html=True)
    risk_level = risk_result.get("risk_level", stress_result.get("risk_level", "UNKNOWN"))
    risk_score = risk_result.get("risk_score", 0)
    st.markdown(
        f"""
        <div class="{get_risk_class(risk_level)}">
            <h3>{risk_level} FINANCIAL RISK</h3>
            <p>Risk score: <strong>{risk_score}/100</strong></p>
            <p>Estimated cash runway: <strong>{stress_result.get('cash_runway_days', 0)} days</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Risk reasons")
    reasons = risk_result.get("reasons", [])
    if reasons:
        for reason in reasons:
            st.write(f"• {reason}")
    else:
        st.write("• No major risk reason was identified.")

    category_expenses = summary.get("category_expenses", {})
    if category_expenses:
        category_df = pd.DataFrame(
            {"Category": list(category_expenses.keys()), "Expense": list(category_expenses.values())}
        )
        chart1, chart2 = st.columns(2)
        with chart1:
            fig_bar = px.bar(
                category_df,
                x="Category",
                y="Expense",
                color="Category",
                title="Expense by Business Category",
            )
            fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Expense Amount (₹)")
            st.plotly_chart(fig_bar, use_container_width=True)
        with chart2:
            fig_pie = px.pie(
                category_df,
                names="Category",
                values="Expense",
                hole=0.55,
                title="Expense Distribution",
            )
            st.plotly_chart(fig_pie, use_container_width=True)


with tabs[1]:
    st.markdown('<div class="section-header">Transaction Intelligence</div>', unsafe_allow_html=True)
    if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
        fcol, scol = st.columns([1, 2])
        categories = (
            sorted(dataframe["category"].dropna().astype(str).unique().tolist())
            if "category" in dataframe.columns
            else []
        )
        with fcol:
            selected_categories = st.multiselect(
                "Filter by category",
                options=categories,
                default=categories,
            )
        with scol:
            search_text = st.text_input(
                "Search transaction description",
                placeholder="Example: rent, supplier or customer",
            )

        filtered_df = dataframe.copy()
        if categories and selected_categories:
            filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
        if search_text and "description" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["description"].astype(str).str.contains(search_text, case=False, na=False)
            ]

        display_columns = [
            "transaction_id", "date", "description", "debit", "credit",
            "balance", "category", "confidence", "category_reason",
        ]
        available_columns = [column for column in display_columns if column in filtered_df.columns]
        st.dataframe(filtered_df[available_columns], use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered_df)} of {len(dataframe)} transactions.")

        st.download_button(
            "⬇️ Download Categorized Transactions",
            data=dataframe.to_csv(index=False).encode("utf-8"),
            file_name="categorized_bank_transactions.csv",
            mime="text/csv",
        )

        if "confidence" in dataframe.columns:
            low_confidence = dataframe[dataframe["confidence"] < 0.70]
            with st.expander(f"Low-confidence transactions ({len(low_confidence)})"):
                if low_confidence.empty:
                    st.success("No low-confidence transactions were found.")
                else:
                    st.dataframe(low_confidence, use_container_width=True, hide_index=True)
    else:
        st.warning("No transaction data is available.")


with tabs[2]:
    st.markdown('<div class="section-header">Cash-Flow Forecast</div>', unsafe_allow_html=True)
    if isinstance(stress_forecast, pd.DataFrame) and not stress_forecast.empty:
        if "baseline_balance" in stress_forecast.columns:
            baseline_column = "baseline_balance"
        elif "projected_balance" in stress_forecast.columns:
            baseline_column = "projected_balance"
        else:
            baseline_column = None

        if baseline_column is None or "stressed_balance" not in stress_forecast.columns:
            st.error("Required forecast balance columns are missing.")
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=stress_forecast["date"],
                    y=stress_forecast[baseline_column],
                    name="Baseline Balance",
                    mode="lines",
                    line={"color": "#0b4f9c", "width": 3},
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=stress_forecast["date"],
                    y=stress_forecast["stressed_balance"],
                    name="Stressed Balance",
                    mode="lines",
                    line={"color": "#d32f2f", "width": 3, "dash": "dash"},
                )
            )
            scenario = stress_result.get("scenario", {})
            fig.add_hline(
                y=scenario.get("safe_balance", 25000),
                line_dash="dot",
                line_color="#f9a825",
                annotation_text="Minimum Safe Balance",
            )
            fig.add_hline(y=0, line_dash="dash", line_color="#263238", annotation_text="Zero Balance")
            fig.update_layout(
                title="Baseline Balance Compared with Stressed Balance",
                xaxis_title="Forecast Date",
                yaxis_title="Projected Balance (₹)",
                hovermode="x unified",
                height=520,
            )
            st.plotly_chart(fig, use_container_width=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Final Stressed Balance", format_inr(stress_result.get("final_stressed_balance", 0)))
            with c2:
                st.metric("Minimum Stressed Balance", format_inr(stress_result.get("minimum_stressed_balance", 0)))
            with c3:
                st.metric("Cash Runway", f"{stress_result.get('cash_runway_days', 0)} days")
    else:
        st.warning("No cash-flow forecast data is available.")


with tabs[3]:
    st.markdown('<div class="section-header">Stress Scenario Result</div>', unsafe_allow_html=True)
    scenario = stress_result.get("scenario", {})
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Revenue Reduction", f"{float(scenario.get('revenue_reduction', 0)):.0f}%")
    with s2:
        st.metric("Expense Increase", f"{float(scenario.get('expense_increase', 0)):.0f}%")
    with s3:
        st.metric("Unexpected Expense", format_inr(scenario.get("unexpected_expense", 0)))
    with s4:
        st.metric("Expense Occurrence", f"Day {scenario.get('unexpected_expense_day', 0)}")

    w1, w2, w3 = st.columns(3)
    with w1:
        st.metric("Stress Risk Level", stress_result.get("risk_level", "UNKNOWN"))
    with w2:
        st.metric("First Low-Balance Date", format_date(stress_result.get("first_low_balance_date")))
    with w3:
        st.metric("First Negative-Balance Date", format_date(stress_result.get("first_negative_balance_date")))

    stress_level = stress_result.get("risk_level", "UNKNOWN")
    if stress_level == "HIGH":
        message = "The balance becomes negative under this scenario. Early intervention and manual review are recommended."
    elif stress_level == "MEDIUM":
        message = "The balance falls below the safe limit. Weekly monitoring is recommended."
    else:
        message = "The account maintains the selected safe cash buffer throughout the forecast period."

    st.markdown(
        f'<div class="{get_risk_class(stress_level)}"><strong>{stress_level} EARLY-WARNING RESULT</strong><p>{message}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### LangChain financial explanation")
    if explanation:
        st.text_area("Financial assessment", value=explanation, height=330, disabled=True)
    else:
        st.info("No explanation is available.")


with tabs[4]:
    st.markdown('<div class="section-header">Voice Intelligence</div>', unsafe_allow_html=True)
    st.write(
        "This module analyzes the SME customer-call transcript for business-risk signals. "
        "A production system can receive the transcript through an Uniphore integration."
    )
    voice_status = voice_result.get("status", "NO_TRANSCRIPT_PROVIDED")
    signal_count = voice_result.get("signal_count", 0)
    v1, v2 = st.columns(2)
    with v1:
        st.metric("Voice Analysis Status", voice_status.replace("_", " ").title())
    with v2:
        st.metric("Financial Signals Detected", signal_count)

    signals = voice_result.get("signals", [])
    if signals:
        st.warning("Financial concerns were detected in the call transcript.")
        voice_df = pd.DataFrame(signals)
        voice_df.columns = [column.replace("_", " ").title() for column in voice_df.columns]
        st.dataframe(voice_df, use_container_width=True, hide_index=True)
    elif voice_status == "NO_TRANSCRIPT_PROVIDED":
        st.info("No customer-call transcript was supplied.")
    else:
        st.success("No major financial concern was identified in the transcript.")

    if signals and risk_result.get("risk_level") in ["HIGH", "MEDIUM"]:
        st.markdown(
            """
            <div class="high-risk">
                <strong>Combined Early-Warning Alert</strong>
                <p>Financial pressure appears in both the statement and call transcript. Relationship-manager review is recommended.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


with tabs[5]:
    st.markdown('<div class="section-header">Technical Workflow</div>', unsafe_allow_html=True)
    st.markdown(
        """
        ### Technologies used
        - **Python:** Core implementation
        - **Pandas:** Transaction processing and financial calculations
        - **Streamlit:** Interactive dashboard
        - **Plotly:** Financial charts
        - **LangGraph:** Workflow orchestration
        - **LangChain:** Controlled financial explanation
        - **Uniphore-ready adapter:** Voice conversation input
        - **Cloud-ready design:** Can later be deployed to Azure
        """
    )

    stages = [
        "1. Statement Loading",
        "2. Statement Validation",
        "3. Transaction Categorization",
        "4. Financial Summary",
        "5. Baseline Forecast",
        "6. Stress Simulation",
        "7. Risk Scoring",
        "8. LangChain Explanation",
        "9. Voice Analysis",
    ]
    st.dataframe(
        pd.DataFrame({"Stage": stages, "Status": ["Completed"] * len(stages)}),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("View complete LangGraph state"):
        safe_state = {}
        for key, value in result.items():
            if isinstance(value, pd.DataFrame):
                safe_state[key] = f"DataFrame containing {len(value)} rows"
            elif key == "stress_result" and isinstance(value, dict):
                safe_stress = value.copy()
                if isinstance(safe_stress.get("forecast"), pd.DataFrame):
                    safe_stress["forecast"] = f"DataFrame containing {len(safe_stress['forecast'])} rows"
                safe_state[key] = safe_stress
            else:
                safe_state[key] = value
        st.json(safe_state)

    st.warning(
        "This application provides decision-support insights only. "
        "Final lending decisions require authorized human review."
    )


st.markdown(
    """
    <div class="footer">
        Smart SME Bank Statement Analyzer | Cash-Flow Stress Simulator | Python + LangGraph + LangChain
    </div>
    """,
    unsafe_allow_html=True,
)
