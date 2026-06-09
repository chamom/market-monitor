import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# ==================================================
# Page Config
# ==================================================

st.set_page_config(layout="wide")

st.markdown("""
<style>

/* 전체 상단 여백 줄이기 */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

/* header 영역 제거 */
header {
    visibility: hidden;
}

/* Streamlit 기본 top space 제거 */
.main {
    padding-top: 0rem !important;
}

/* 메뉴 숨김 (선택) */
#MainMenu {
    visibility: hidden;
}

/* footer 숨김 */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="GBD Cockpit",
    layout="centered"
)

# ==================================================
# Header
# ==================================================

header1, header2 = st.columns([3, 1])

with header1:
    st.markdown("Market Monitor")

with header2:
    st.metric(
        "System Update",
        pd.Timestamp.now().strftime("%Y-%m-%d")
    )

st.divider()

# ==================================================
# Common Functions
# ==================================================

@st.cache_data(ttl=3600)
def get_latest_price(ticker_symbol):

    ticker = yf.Ticker(ticker_symbol)

    hist = ticker.history(period="5d")

    if hist.empty:
        return None, None

    current = round(hist["Close"].iloc[-1], 2)
    previous = round(hist["Close"].iloc[-2], 2)

    change = round(
        ((current - previous) / previous) * 100,
        2
    )

    return current, change


@st.cache_data(ttl=3600)
def load_market_data(ticker_symbol):

    ticker = yf.Ticker(ticker_symbol)

    return ticker.history(period="1y")


def render_market_tab(
    title,
    ticker_map,
    key_name
):

    st.header(title)

    indicator = st.segmented_control(
        "Indicator",
        list(ticker_map.keys()),
        default=list(ticker_map.keys())[0],
        key=key_name
    )

    hist = load_market_data(
        ticker_map[indicator]
    )

    if hist.empty:
        st.error("Unable to retrieve data.")
        return

    current = round(
        hist["Close"].iloc[-1],
        2
    )

    one_month = round(
        hist["Close"].iloc[-22],
        2
    )

    three_month = round(
        hist["Close"].iloc[-66],
        2
    )

    change_1m = round(
        ((current - one_month) / one_month) * 100,
        2
    )

    change_3m = round(
        ((current - three_month) / three_month) * 100,
        2
    )

    latest_date = hist.index[-1].strftime(
        "%Y-%m-%d"
    )

    st.caption(
        f"Latest Market Data : {latest_date}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Current",
            current
        )

    with col2:
        st.metric(
            "1M Change",
            f"{change_1m}%"
        )

    with col3:
        st.metric(
            "3M Change",
            f"{change_3m}%"
        )

    fig = px.line(
        hist,
        x=hist.index,
        y="Close",
        title=f"{indicator} - Last 12 Months"
    )

    fig.update_layout(
        height=500,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    summary = pd.DataFrame({
        "Metric": [
            "Current",
            "52W High",
            "52W Low",
            "1M Change",
            "3M Change"
        ],
        "Value": [
            current,
            round(hist["Close"].max(), 2),
            round(hist["Close"].min(), 2),
            f"{change_1m}%",
            f"{change_3m}%"
        ]
    })

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# Overview Data
# ==================================================

usd_value, usd_change = get_latest_price("KRW=X")
wti_value, wti_change = get_latest_price("CL=F")
copper_value, copper_change = get_latest_price("HG=F")
corn_value, corn_change = get_latest_price("ZC=F")

# ==================================================
# Tabs
# ==================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Finance",
    "Logistics",
    "Cost",
    "Demand"
])

# ==================================================
# Overview
# ==================================================

with tab1:

    st.subheader("Business Health")

    health1, health2 = st.columns(2)

    with health1:
        st.success("Demand | Favorable")

    with health2:
        st.warning("Finance | Neutral")

    health3, health4 = st.columns(2)

    with health3:
        st.success("Supply Chain | Stable")

    with health4:
        st.error("Production Cost | Watch")

    st.divider()

    st.subheader("Key Indicators")

    st.caption(
        "Change vs Previous Trading Day"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "USD/KRW",
            usd_value,
            f"{usd_change}%"
        )

    with col2:
        st.metric(
            "Corn",
            corn_value,
            f"{corn_change}%"
        )

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "WTI",
            wti_value,
            f"{wti_change}%"
        )

    with col4:
        st.metric(
            "Copper",
            copper_value,
            f"{copper_change}%"
        )

# ==================================================
# Finance
# ==================================================

with tab2:

    render_market_tab(
        "Finance",
        {
            "USD/KRW": "KRW=X",
            "CAD/KRW": "CADKRW=X",
            "EUR/KRW": "EURKRW=X",
            "US10Y": "^TNX"
        },
        "finance_indicator"
    )

# ==================================================
# Logistics
# ==================================================

with tab3:

    render_market_tab(
        "Logistics",
        {
            "WTI": "CL=F",
            "Brent": "BZ=F",
            "Natural Gas": "NG=F"
        },
        "logistics_indicator"
    )

# ==================================================
# Cost
# ==================================================

with tab4:

    render_market_tab(
        "Production Cost",
        {
            "Copper": "HG=F"
        },
        "cost_indicator"
    )

# ==================================================
# Demand
# ==================================================

with tab5:

    render_market_tab(
        "Farm Economics & Demand",
        {
            "Corn": "ZC=F",
            "Soybean": "ZS=F",
            "Wheat": "ZW=F"
        },
        "demand_indicator"
    )