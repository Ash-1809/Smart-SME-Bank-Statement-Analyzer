VOICE_SIGNALS = {
    "Customer Payment Delay": [
        "customer delayed payment",
        "payment is delayed",
        "invoice is pending",
        "payment has not arrived",
        "client has not paid",
    ],
    "Revenue Reduction": [
        "sales have decreased",
        "revenue has reduced",
        "fewer customer orders",
        "business is slow",
    ],
    "Supplier Pressure": [
        "supplier is demanding payment",
        "supplier payment is pending",
        "vendor is asking for payment",
    ],
    "EMI Difficulty": [
        "unable to pay emi",
        "emi may be delayed",
        "loan payment difficulty",
    ],
    "Unexpected Expense": [
        "machine repair",
        "unexpected expense",
        "equipment replacement",
        "emergency payment",
    ],
}


def analyze_voice_transcript(transcript: str) -> dict:
    """Extract business-risk signals from a call transcript."""

    normalized_text = transcript.lower()
    detected_signals = []

    for signal, phrases in VOICE_SIGNALS.items():
        for phrase in phrases:
            if phrase in normalized_text:
                detected_signals.append({
                    "signal": signal,
                    "matched_phrase": phrase,
                })
                break

    if detected_signals:
        status = "FINANCIAL_CONCERN_DETECTED"
    else:
        status = "NO_MAJOR_CONCERN_DETECTED"

    return {
        "status": status,
        "signals": detected_signals,
        "signal_count": len(detected_signals),
    }