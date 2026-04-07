import io
import time
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional

# Import the multi-agent system from our new CIO file
from chief_investment_officer_agent import run_multi_agent_system

# Import libraries specifically for generating the PDF report
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# ==========================================
# PAGE SETUP
# ==========================================
st.set_page_config(page_title="Pro Investor System", layout="wide")

# ==========================================
# DATA FETCHING
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_market_data(ticker: str, timeframe: str = "6mo") -> Optional[Dict[str, Any]]:
    try:
        obj = yf.Ticker(ticker)
        hist = obj.history(period=timeframe)

        if hist.empty:
            return None

        hist["Returns"] = hist["Close"].pct_change()
        pe_ratio = obj.info.get("trailingPE")
        pe_ratio = round(pe_ratio, 2) if isinstance(pe_ratio, (int, float)) else "N/A"

        std_dev = hist["Returns"].std()
        sharpe = 0.0 if pd.isna(std_dev) or std_dev == 0 else round((hist["Returns"].mean() / std_dev) * np.sqrt(252), 2)

        cumulative_returns = (1 + hist["Returns"].fillna(0)).cumprod()
        rolling_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = round(drawdown.min() * 100, 2) if not drawdown.empty else 0.0

        return {
            "symbol": ticker.upper(),
            "return": round(((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100, 2),
            "volatility": round(std_dev * np.sqrt(252) * 100, 2) if not pd.isna(std_dev) else 0.0,
            "sharpe": sharpe,
            "max_drawdown": max_drawdown,
            "pe": pe_ratio,
            "data": hist
        }
    except Exception as e:
        st.warning(f"Could not fetch data for {ticker}: {str(e)}")
        return None

# ==========================================
# HELPER: CHART FOR PDF
# ==========================================
def create_pdf_chart(all_data: List[Dict[str, Any]]) -> io.BytesIO:
    plt.figure(figsize=(7, 4))
    for d in all_data:
        norm_price = (d["data"]["Close"] / d["data"]["Close"].iloc[0]) * 100
        plt.plot(d["data"].index, norm_price, label=d["symbol"], linewidth=1.5)

    plt.title("Asset Growth Comparison (Base 100)", pad=15)
    plt.ylabel("Normalized Value")
    plt.legend(loc='upper left', fontsize='small')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    img_buf.seek(0)
    return img_buf

# ==========================================
# PDF EXPORT
# ==========================================
def export_pdf_report(data: List[Dict[str, Any]], narrative: str) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Investment Analysis Executive Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    table_data = [["Asset", "Return (%)", "Volatility (%)", "Max Drawdown (%)", "Sharpe", "P/E"]]
    for d in data:
        table_data.append([
            d["symbol"],
            f"{d['return']}%",
            f"{d['volatility']}%",
            f"{d['max_drawdown']}%",
            str(d['sharpe']),
            str(d['pe'])
        ])

    pdf_table = Table(table_data, colWidths=[75, 75, 80, 85, 65, 65])
    pdf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ff4b4b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(Paragraph("1. Performance Metrics Overview", styles["Heading2"]))
    elements.append(pdf_table)
    elements.append(Spacer(1, 25))

    elements.append(Paragraph("2. Visual Market Trend", styles["Heading2"]))
    chart_img = create_pdf_chart(data)
    elements.append(Image(chart_img, width=450, height=257))
    elements.append(Spacer(1, 25))

    elements.append(Paragraph("3. Multi-Agent AI Investment Decision", styles["Heading2"]))
    for line in narrative.split('\n'):
        if line.strip():
            elements.append(Paragraph(line, styles["Normal"]))
            elements.append(Spacer(1, 6))

    doc.build(elements)
    buf.seek(0)
    return buf

# ==========================================
# MAIN USER INTERFACE
# ==========================================
def main():
    st.title("🤖 Agentic AI-Driven Multi-Agent Framework for Financial Data Analysis")
    st.markdown("Analyze assets, compare performance, and generate AI-driven reports.")

    with st.sidebar:
        st.header("Configuration")
        with st.form("input_form"):
            ticker_input = st.text_input("Enter Stocks (Comma Separated)", "AAPL, TSLA, GOOG")
            timeframe = st.selectbox("Timeframe", ["3mo", "6mo", "1y", "2y", "5y"], index=1)
            trigger = st.form_submit_button("Run Multi-Agent Analysis", use_container_width=True)

    if trigger:
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

        if not tickers:
            st.warning("Please enter at least one valid ticker symbol.")
            return

        processed_data = []

        with st.spinner("Fetching Market Data & Initializing Agents..."):
            for t in tickers:
                d = fetch_market_data(t, timeframe)
                if d:
                    processed_data.append(d)

        if not processed_data:
            st.error("Could not retrieve data for any of the entered tickers.")
            return

        st.subheader("Performance Overview")
        cols = st.columns(len(processed_data))
        for i, entry in enumerate(processed_data):
            with cols[i]:
                st.metric(
                    label=f"🚀 {entry['symbol']}",
                    value=f"{entry['return']}%",
                    delta=f"Sharpe: {entry['sharpe']}",
                    delta_color="normal" if entry['sharpe'] > 0 else "inverse"
                )

        st.divider()

        st.markdown("### Key Statistics")
        df_display = pd.DataFrame(processed_data).drop(columns=['data'])
        df_display.rename(columns={
            "symbol": "Asset",
            "return": "Return (%)",
            "volatility": "Volatility (%)",
            "sharpe": "Sharpe Ratio",
            "max_drawdown": "Max Drawdown (%)",
            "pe": "P/E Ratio"
        }, inplace=True)
        df_display = df_display[["Asset", "Return (%)", "Volatility (%)", "Max Drawdown (%)", "Sharpe Ratio", "P/E Ratio"]]
        st.dataframe(df_display, hide_index=True, use_container_width=True)

        st.divider()

        st.markdown("### Price Action & 50-Day Moving Average")
        fig = go.Figure()

        for d in processed_data:
            df = d["data"]
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name=f"{d['symbol']} Close", line=dict(width=2)))

            if len(df) >= 50:
                sma_50 = df["Close"].rolling(window=50).mean()
                fig.add_trace(go.Scatter(x=df.index, y=sma_50, mode='lines', name=f"{d['symbol']} 50d SMA", line=dict(width=1.5, dash='dot'), opacity=0.7))

        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="Stock Price (USD)"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("Multi-Agent Committee Decision")

        progress_text = "Agents are autonomously analyzing data. Please wait."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)

        # Call the imported multi-agent function
        result = run_multi_agent_system(processed_data)
        my_bar.empty()

        st.markdown("#### Individual Analyst Reports")
        with st.expander("Agent 1: Value Analyst"):
            st.info(result["value"])
        with st.expander("Agent 2: Risk Analyst"):
            st.warning(result["risk"])
        with st.expander("Agent 3: Momentum Analyst"):
            st.success(result["momentum"])

        st.markdown("#### Chief Investment Officer (Final Verdict)")
        with st.container(border=True):
            st.markdown(result["cio"])

        pdf_report = export_pdf_report(processed_data, result["cio"])

        # FIXED: Removed the repeated 'label' argument
        st.download_button(
            label="Download Comprehensive PDF Report",
            data=pdf_report,
            file_name="Multi_Agent_Investment_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

if __name__ == "__main__":
    main()