import streamlit as st
import importlib
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from shareconf import llm
from value import agent_value_analyst
from risk import agent_risk_analyst

# Using importlib to import files that have spaces in their names
momentum_module = importlib.import_module("movementum anal")
agent_momentum_analyst = momentum_module.agent_momentum_analyst

news_module = importlib.import_module("news analyst")
agent_news_sentiment = news_module.agent_news_sentiment

def run_multi_agent_system(all_data: List[Dict[str, Any]], news_summary_str: str, strategy: str) -> Dict[str, str]:
    # Reset states
    st.session_state['val_report'] = "Tool not called by agent."
    st.session_state['risk_report'] = "Tool not called by agent."
    st.session_state['mom_report'] = "Tool not called by agent."
    st.session_state['news_report'] = "Tool not called by agent (News ignored for 3 Year TF)."

    data_str = "\n".join([f"Asset: {d['symbol']}, Return: {d['return']}%, Volatility: {d['volatility']}%, Max Drawdown: {d['max_drawdown']}%, Sharpe: {d['sharpe']}, P/E: {d['pe']}" for d in all_data])

    # Base Tools for all timeframes
    tools = [agent_value_analyst, agent_risk_analyst, agent_momentum_analyst]

    # Conditionally inject the 4th Agent and strict formatting templates
    if strategy == "6 Month":
        tools.append(agent_news_sentiment)
        strategy_instruction = """This is a SHORT-TERM 6 Month strategy. 
        CRITICAL RULE 1: You MUST autonomously call ALL FOUR tools (`agent_value_analyst`, `agent_risk_analyst`, `agent_momentum_analyst`, and `agent_news_sentiment`). 
        CRITICAL RULE 2: You MUST pass the 'RAW NEWS HEADLINES' exactly as provided to the `agent_news_sentiment` tool."""
        input_string = f"MARKET DATA:\n{data_str}\n\nRAW NEWS HEADLINES (Pass this string to agent_news_sentiment):\n{news_summary_str}"

        format_instruction = """
        YOU MUST STRICTLY USE THIS EXACT MARKDOWN TEMPLATE FOR YOUR FINAL RESPONSE:
        
        **FINAL INVESTMENT SUMMARY**
        [Write a highly compact synthesis. Provide one short paragraph per asset (about 2-3 lines each). In each paragraph, seamlessly combine the findings from the Value, Risk, Momentum, and News analysts to give a complete picture of that asset.]
        
        **FINAL VERDICT**
        [Your definitive 1-2 sentence final recommendation based on the combined data.]
        """
    else:
        strategy_instruction = """This is a LONG-TERM 3 Year strategy. 
        CRITICAL RULE 1: You MUST autonomously call ALL THREE tools (`agent_value_analyst`, `agent_risk_analyst`, `agent_momentum_analyst`). 
        CRITICAL RULE 2: You MUST prioritize the mathematical fundamentals and macro data. Ignore daily news completely."""
        input_string = f"MARKET DATA:\n{data_str}"

        format_instruction = """
        YOU MUST STRICTLY USE THIS EXACT MARKDOWN TEMPLATE FOR YOUR FINAL RESPONSE:
        
        **FINAL INVESTMENT SUMMARY**
        [Write a highly compact synthesis. Provide one short paragraph per asset (about 2-3 lines each). In each paragraph, seamlessly combine the findings from the Value, Risk, and Momentum analysts to give a complete picture of that asset.]
        
        **FINAL VERDICT**
        [Your definitive 1-2 sentence final recommendation based on the combined data.]
        """

    system_prompt = (
        f"You are an Autonomous Chief Investment Officer (CIO) executing a {strategy} strategy.\n"
        "You have several analytical tools at your disposal.\n\n"
        "INSTRUCTIONS:\n"
        f"1. {strategy_instruction}\n"
        "2. Wait for the tools to return their specific analytical reports.\n"
        "3. Read the returned reports carefully.\n"
        f"4. {format_instruction}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Here is the raw data. Begin your autonomous analysis:\n{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"input": input_string})

    return {
        "value": st.session_state['val_report'],
        "risk": st.session_state['risk_report'],
        "momentum": st.session_state['mom_report'],
        "news": st.session_state['news_report'],
        "cio": response["output"]
    }