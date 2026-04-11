import streamlit as st
from langchain_core.tools import tool
from shareconf import llm

@tool
def agent_momentum_analyst(data_str: str) -> str:
    """Use this tool to analyze the Return (%) and price momentum."""
    prompt = f"You are Agent 3: The Momentum Analyst. Analyze the Return (%) and price momentum. Keep it to 3-4 sentences.\nData: {data_str}"
    response = llm.invoke(prompt).content
    st.session_state['mom_report'] = response
    return response