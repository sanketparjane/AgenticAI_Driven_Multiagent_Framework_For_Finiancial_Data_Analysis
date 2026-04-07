import streamlit as st
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from shared_configuration import get_llm

# Import the 3 sub-agents using their full names
from value_analyst_agent import agent_value_analyst
from risk_analyst_agent import agent_risk_analyst
from momentum_analyst_agent import agent_momentum_analyst

def run_multi_agent_system(all_data: List[Dict[str, Any]]) -> Dict[str, str]:
    llm = get_llm()

    # Initialize the session state so UI doesn't crash if an agent skips a tool
    st.session_state['val_report'] = "Tool not called by agent."
    st.session_state['risk_report'] = "Tool not called by agent."
    st.session_state['mom_report'] = "Tool not called by agent."

    # Format the data so the AI can read it easily
    data_str = "\n".join([f"Asset: {d['symbol']}, Return: {d['return']}%, Volatility: {d['volatility']}%, Max Drawdown: {d['max_drawdown']}%, Sharpe: {d['sharpe']}, P/E: {d['pe']}" for d in all_data])

    # Give the CIO agent access to the tools
    tools = [agent_value_analyst, agent_risk_analyst, agent_momentum_analyst]

    # Set up the Autonomous CIO Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Autonomous Chief Investment Officer (CIO).
        You have three analytical tools at your disposal: agent_value_analyst, agent_risk_analyst, and agent_momentum_analyst.
        
        INSTRUCTIONS:
        1. You MUST autonomously call ALL THREE tools to analyze the provided market data. Pass the data to the tools.
        2. Wait for the tools to return their specific analytical reports.
        3. Once you have all three perspectives, synthesize them into a highly detailed, comprehensive final investment summary.
        4. Structure your response with clear headings. Declare a clear winner based on the combined data. Plain text only.
        """),
        ("human", "Here is the raw market data. Begin your autonomous analysis:\n{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Construct and run the Autonomous Agent Loop
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"input": data_str})

    # Return the dictionary exactly as the UI expects it
    return {
        "value": st.session_state['val_report'],
        "risk": st.session_state['risk_report'],
        "momentum": st.session_state['mom_report'],
        "cio": response["output"]
    }