
# Agentic AI-Driven Multi-Agent Financial Data Analysis 

## 📌 Overview

This project is a Streamlit-based web application that combines financial data analysis with an autonomous multi-agent AI system. It allows users to analyze multiple stocks, compare their performance, and generate an AI-driven investment report — all in one place.

The system is designed to simulate how different types of financial analysts work together and then produce a final decision, similar to a real-world investment committee.

---

## Key Features

* Real-Time Market Data
  Fetches stock data using Yahoo Finance for selected timeframes.

* Performance Metrics Calculation
  Automatically computes:

  * Returns (%)
  * Volatility (%)
  * Sharpe Ratio
  * Maximum Drawdown (%)
  * P/E Ratio

* Interactive Visualization

  * Price charts with 50-day moving average
  * Multi-asset comparison graphs

* Multi-Agent AI System
  Three specialized AI agents analyze the data:

  * Value Analyst → focuses on valuation (P/E)
  * Risk Analyst → evaluates volatility, drawdown, Sharpe
  * Momentum Analyst → analyzes returns and trends

* Autonomous CIO Agent
  A main AI agent:

  * Calls all sub-agents automatically
  * Combines their insights
  * Produces a final investment decision

* PDF Report Generation
  Generates a professional report including:

  * Performance table
  * Market trend chart
  * AI-generated investment summary

---

##  System Architecture

```
User Input → Data Fetching → Metric Calculation
                     ↓
           Multi-Agent AI System
        (Value + Risk + Momentum)
                     ↓
           Chief Investment Officer
                     ↓
        Final Decision + PDF Report
```

---

##  How the Multi-Agent System Works

1. The system collects processed financial data.
2. The main agent (CIO) is initialized with access to three tools (agents).
3. Each agent is called automatically:

   * Value Agent analyzes valuation
   * Risk Agent evaluates risk metrics
   * Momentum Agent studies returns
4. Their outputs are combined.
5. The CIO agent generates a final structured investment summary.

This makes the system agentic, meaning it independently decides how to use tools rather than following a fixed sequence.

---

## 🛠️ Tech Stack

* Frontend/UI: Streamlit
* Data Source: Yahoo Finance (yfinance)
* Visualization: Plotly, Matplotlib
* AI/LLM: Groq (LLaMA 3.1 8B Instant)
* Agent Framework: LangChain
* PDF Generation: ReportLab
* Data Processing: Pandas, NumPy

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sanketparjane/AgenticAI_Driven_Multiagent_Framework_For_Finiancial_Data_Analysis/tree/main
cd your-repo-name
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Environment Variables

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_api_key_here
```

### 4. Run the Application

```bash
streamlit run app.py
```

---

## 📊 Usage

1. Enter stock tickers (comma-separated)
   Example: `AAPL, TSLA, GOOG`
2. Select timeframe
3. Click **Run Multi-Agent Analysis**
4. View:

   * Performance metrics
   * Charts
   * AI analysis
5. Download the PDF report

---

## 📁 Project Structure

```
├── app.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🎯 Use Cases

* Personal stock analysis
* Learning financial metrics
* Understanding multi-agent AI systems
* Building AI-powered fintech projects

---

## ⚠️ Disclaimer

This project is for educational and informational purposes only.
It does not provide financial advice. Always do your own research before making investment decisions.

---

## 💡 Future Improvements

* Portfolio optimization
* More technical indicators
* Real-time streaming data

---

## 👨‍💻 Author
Sanket Parjane  

This project demonstrates practical implementation of multi-agent AI systems applied to financial data analysis, combining LLMs with real-time market insights.

---
