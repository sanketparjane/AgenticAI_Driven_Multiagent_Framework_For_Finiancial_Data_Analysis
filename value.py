import streamlit as st
from langchain_core.tools import tool
from shareconf import llm

@tool
def agent_value_analyst(data_str: str) -> str:
    """Use this tool to analyze the P/E ratios and valuations of the assets."""
    prompt = f"You are Agent 1: The Value Analyst. Analyze the P/E ratios and valuations of these assets. Keep it to 3-4 sentences.\nData: {data_str}"
    response = llm.invoke(prompt).content
    st.session_state['val_report'] = response
    return response