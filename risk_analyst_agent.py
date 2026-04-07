import streamlit as st
from langchain_core.tools import tool
from shared_configuration import get_llm

@tool
def agent_risk_analyst(data_str: str) -> str:
    """Use this tool to analyze the Volatility, Max Drawdown, and Sharpe ratios to determine risk-adjusted performance."""
    llm = get_llm()
    prompt = f"You are Agent 2: The Risk Analyst. Analyze the Volatility, Max Drawdown, and Sharpe ratios to determine risk-adjusted performance. Keep it to 9 sentences.\nData: {data_str}"

    response = llm.invoke(prompt).content
    st.session_state['risk_report'] = response
    return response