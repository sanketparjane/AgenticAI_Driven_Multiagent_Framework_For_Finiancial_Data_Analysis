import streamlit as st
from langchain_core.tools import tool
from shareconf import llm

@tool
def agent_news_sentiment(news_str: str) -> str:
    """CRITICAL: You MUST use this tool to evaluate news data. Pass the raw news string to this tool to determine if there is a 'Boom' or short-term momentum catalyst."""
    prompt = f"You are Agent 4: The News Sentiment Analyst. Review the following recent news headlines. Determine if the news indicates a positive momentum catalyst (Boom) or a negative/neutral outlook. Keep it to 3-4 sentences.\nData: {news_str}"
    response = llm.invoke(prompt).content
    st.session_state['news_report'] = response
    return response