import os
import io
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# ==========================================
# ENVIRONMENT & AI INITIALIZATION
# ==========================================
load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")

@st.cache_resource
def get_llm():
    if not GROQ_KEY:
        st.error("GROQ API Key Missing. Please check your .env file.")
        st.stop()
    return ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_KEY, temperature=0.1)

llm = get_llm()

# ==========================================
# DATA FETCHING
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_market_data(ticker: str, timeframe: str) -> Optional[Dict[str, Any]]:
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
# PDF EXPORT HELPERS
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