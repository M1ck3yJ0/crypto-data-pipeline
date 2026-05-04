"""
streamlit/app.py
Crypto Market Intelligence Dashboard
Reads from data/coingecko_markets.csv (GitHub raw URL)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Market Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── UNIVERSAL DESIGN SETTINGS ────────────────────────────────────────────────
APP_THEME = {
    "font": {
        "body": "Syne",
        "body_stack": "Syne, sans-serif",
        "mono": "DM Mono",
        "mono_stack": "DM Mono, monospace",
        "base_size": 13,
        "chart_size": 10,
        "chart_title_size": 12,
        "metric_size": 22,
    },
    "color": {
        "page_bg": "#020817",
        "panel_bg": "#0a1628",
        "card_bg": "#0f172a",
        "metric_bg": "#0d1f3c",
        "border": "#1e293b",
        "subtle_border": "#0f172a",
        "text": "#e2e8f0",
        "muted": "#94a3b8",
        "faint": "#64748b",
        "title": "#cbd5e1",
        "chart_title": "#94a3b8",
        "accent": "#336ba8",
        "accent_2": "#0d9488",
        "accent_3": "#134e4a",
        "positive": "#2dd4bf",
        "positive_2": "#0d9488",
        "positive_3": "#134e4a",
        "negative": "#f87171",
        "negative_2": "#ef4444",
        "negative_3": "#b91c1c",
    },
    "chart": {
        "height": 280,
        "margin": dict(l=12, r=12, t=28, b=12),
        "line_width": 1.5,
        "thin_line_width": 1,
        "fill_alpha_light": 0.05,
        "fill_alpha": 0.10,
        "bar_alpha": 0.30,
        "legend_size": 9,
    },
    "layout": {
        "section_top_margin": "1.5rem",
        "divider_margin": "1.2rem 0",
        "border_radius": "8px",
    },
}

COLORS = APP_THEME["color"]
FONTS = APP_THEME["font"]
CHART = APP_THEME["chart"]

SEQUENTIAL_PALETTE = [
    COLORS["accent"],
    COLORS["accent_2"],
    COLORS["accent_3"],
    COLORS["border"],
    COLORS["card_bg"],
    "#334155",
    "#475569",
    "#5f799f",
    "#6785a7",
    COLORS["muted"],
]

RETURN_COLORS = {
    "1d": COLORS["accent"],
    "7d": COLORS["accent_2"],
    "30d": COLORS["accent_3"],
}

NEGATIVE_RETURN_COLORS = {
    "1d": COLORS["negative"],
    "7d": COLORS["negative_2"],
    "30d": COLORS["negative_3"],
}


def rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex color to rgba() so transparency is controlled in one place."""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"

def style_table(table_df: pd.DataFrame):
    return (
        table_df.style
        .hide(axis="index")
        .set_properties(**{
            "background-color": COLORS["panel_bg"],
            "color": COLORS["text"],
            "border-color": COLORS["border"],
            "font-family": FONTS["mono"],
            "font-size": "12px",
        })
        .set_table_styles([
            {
                "selector": "thead th, thead th div, thead th span",
                "props": [
                    ("background-color", f"{COLORS['card_bg']} !important"),
                    ("color", f"{COLORS['muted']} !important"),
                    ("font-family", FONTS["mono"]),
                    ("font-size", "11px"),
                    ("text-transform", "uppercase"),
                    ("letter-spacing", "0.08em"),
                    ("border-color", COLORS["border"]),
                ],
            },
            {
                "selector": "tbody td",
                "props": [
                    ("background-color", COLORS["panel_bg"]),
                    ("color", COLORS["text"]),
                    ("border-color", COLORS["border"]),
                ],
            },
        ])
    )

def inject_css() -> None:
    """Apply Streamlit styling from APP_THEME."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: '{FONTS['body']}', sans-serif;
            background-color: {COLORS['page_bg']};
            color: {COLORS['muted']};
            font-size: {FONTS['base_size']}px;
        }}
        .stApp {{ background-color: {COLORS['page_bg']}; }}
        #MainMenu, footer, header {{ visibility: hidden; }}

        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background-color: {COLORS['panel_bg']} !important;
            color: {COLORS['text']} !important;
            border: 1px solid {COLORS['border']} !important;
        }}

        [data-testid="stSelectbox"] div[data-baseweb="select"] span {{
            color: {COLORS['text']} !important;
        }}

        [data-testid="stSelectbox"] label {{
            color: {COLORS['muted']} !important;
            font-family: '{FONTS['mono']}', monospace !important;
            font-size: 0.65rem !important;
        }}

        [data-testid="metric-container"] {{
            background: {COLORS['metric_bg']};
            border: 1px solid {COLORS['border']};
            border-radius: {APP_THEME['layout']['border_radius']};
            padding: 0.8rem 1rem;
            opacity: 1 !important;
        }}
        [data-testid="metric-container"] label,
        [data-testid="metric-container"] label *,
        [data-testid="metric-container"] p,
        [data-testid="metric-container"] p *,
        [data-testid="metric-container"] [data-testid="stMetricLabel"],
        [data-testid="metric-container"] [data-testid="stMetricLabel"] * {{
            font-family: '{FONTS['mono']}', monospace !important;
            font-size: 0.6rem !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
            color: {COLORS['muted']} !important;
            opacity: 1 !important;
        }}
        [data-testid="stMetricValue"] div,
        [data-testid="stMetricValue"] {{
            font-family: '{FONTS['body']}', sans-serif !important;
            font-size: {FONTS['metric_size']}px !important;
            font-weight: 700 !important;
            color: {COLORS['text']} !important;
            opacity: 1 !important;
        }}
        [data-testid="stMetricDelta"] {{
            font-family: '{FONTS['mono']}', monospace !important;
            font-size: 0.65rem !important;
            opacity: 1 !important;
        }}

        .dash-header {{
            padding: 1.2rem 0 1rem 0;
            border-bottom: 1px solid {COLORS['subtle_border']};
            margin-bottom: 1.2rem;
        }}
        .dash-title {{
            font-family: '{FONTS['body']}', sans-serif;
            font-size: 4.4rem;
            font-weight: 900;
            color: {COLORS['title']};
            letter-spacing: 0.01em;
            text-align: center;
            margin: 0 0 2.8rem 0;
            line-height: 4.25;
        }}
        .dash-meta-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            font-family: '{FONTS['mono']}', monospace;
            font-size: 0.7rem;
            color: {COLORS['muted']};
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-top: 0.25rem;
        }}
        .dash-meta-left {{
            text-align: left;
        }}
        .dash-meta-right {{
            text-align: right;
        }}
        .section-label {{
            font-family: '{FONTS['mono']}', monospace;
            font-size: 0.6rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: {COLORS['faint']};
            margin-bottom: 0.4rem;
            margin-top: {APP_THEME['layout']['section_top_margin']};
            border-left: 2px solid {COLORS['accent']};
            padding-left: 0.5rem;
        }}
        .sub-label {{
            font-family: '{FONTS['mono']}', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }}
        .positive-label {{ color: {COLORS['positive']}; }}
        .negative-label {{ color: {COLORS['negative']}; }}
        .section-divider {{
            border: none;
            border-top: 1px solid {COLORS['subtle_border']};
            margin: {APP_THEME['layout']['divider_margin']};
        }}
        [data-testid="stDataFrame"] {{
            background: {COLORS['panel_bg']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: {APP_THEME['layout']['border_radius']} !important;
            font-size: 0.75rem !important;
        }}

        div[data-testid="stDataFrame"] [role="columnheader"],
        div[data-testid="stDataFrame"] [role="columnheader"] * {{
            background-color: {COLORS['card_bg']} !important;
            color: {COLORS['muted']} !important;
        }}
        [data-testid="stTabs"] button {{
            font-family: '{FONTS['mono']}', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #5f799f;
            padding: 0.3rem 0.6rem;
        }}
        [data-testid="stTabs"] button[aria-selected="true"] {{
            color: #93c5fd;
            border-bottom-color: {COLORS['accent']};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def base_plotly_layout(height: int | None = None) -> dict:
    """Shared Plotly layout. Use this for every chart."""
    return dict(
        paper_bgcolor=COLORS["panel_bg"],
        plot_bgcolor=COLORS["panel_bg"],
        font=dict(
            family=FONTS["mono_stack"],
            color=COLORS["muted"],
            size=FONTS["chart_size"],
        ),
        title_font=dict(
            family=FONTS["mono_stack"],
            color=COLORS["title"],
            size=FONTS["chart_title_size"],
        ),
        margin=CHART["margin"],
        height=height or CHART["height"],
        xaxis=dict(
            gridcolor=COLORS["subtle_border"],
            linecolor=COLORS["subtle_border"],
            tickcolor=COLORS["subtle_border"],
            zerolinecolor=COLORS["subtle_border"],
        ),
        yaxis=dict(
            gridcolor=COLORS["subtle_border"],
            linecolor=COLORS["subtle_border"],
            tickcolor=COLORS["subtle_border"],
            zerolinecolor=COLORS["subtle_border"],
        ),
    )


def style_chart(fig: go.Figure, *, title: str | None = None, showlegend: bool = False, height: int | None = None) -> go.Figure:
    """Apply one consistent chart style after each figure is created."""
    fig.update_layout(
        **base_plotly_layout(height=height),
        title=dict(
            text=title,
            x=0.5,
            xanchor="center",
            font=dict(
                family=FONTS["mono_stack"],
                color=COLORS["chart_title"],
                size=FONTS["chart_title_size"],
            ),
        ),
        showlegend=showlegend,
        legend=dict(
            font=dict(size=CHART["legend_size"], color=COLORS["muted"]),
            bgcolor=COLORS["card_bg"],
            bordercolor=COLORS["border"],
            borderwidth=1,
        ),
    )
 
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
 
    return fig


def section_label(text: str) -> None:
    st.markdown(f'<p class="section-label">{text}</p>', unsafe_allow_html=True)


def divider() -> None:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


def sub_label(text: str, tone: str = "positive") -> None:
    class_name = "positive-label" if tone == "positive" else "negative-label"
    st.markdown(f'<p class="sub-label {class_name}">{text}</p>', unsafe_allow_html=True)


inject_css()

# ── DATA LOADING ──────────────────────────────────────────────────────────────
DATA_URL = "https://raw.githubusercontent.com/M1ck3yJ0/crypto-data-pipeline/main/data/coingecko_markets.csv"


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)
    df["date"] = pd.to_datetime(df["date"])
    df["market_cap_b"] = df["market_cap"] / 1e9
    df["total_volume_b"] = df["total_volume"] / 1e9
    return df


df = load_data()
latest_date = df["date"].max()
latest = df[df["date"] == latest_date].copy()
prev_dates = sorted(df["date"].unique())
prev_date_1d = prev_dates[-2] if len(prev_dates) >= 2 else latest_date
prev = df[df["date"] == prev_date_1d].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="dash-header">
      <p class="dash-title">Crypto Market Intelligence</p>
      <div class="dash-meta-row">
        <span class="dash-meta-left">
          Universe: Top 50 coins · Fixed 2025-12-01
        </span>
        <span class="dash-meta-right">
          Last updated: {latest_date.strftime('%Y-%m-%d')} · {df['date'].nunique()} days of history
        </span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total_mcap = latest["market_cap"].sum()
prev_mcap = prev["market_cap"].sum()
mcap_delta = ((total_mcap - prev_mcap) / prev_mcap) * 100 if prev_mcap else 0

total_vol = latest["total_volume"].sum()
prev_vol = prev["total_volume"].sum()
vol_delta = ((total_vol - prev_vol) / prev_vol) * 100 if prev_vol else 0

btc_mcap = latest.loc[latest["id"] == "bitcoin", "market_cap"].values
btc_dom = (btc_mcap[0] / total_mcap * 100) if len(btc_mcap) > 0 and total_mcap else 0

coins_up_7d = (latest["price_change_percentage_7d_in_currency"] > 0).sum()
breadth = f"{coins_up_7d} / {len(latest)}"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total Market Cap", f"${total_mcap / 1e12:.2f}T", f"{mcap_delta:+.2f}% vs yesterday")
with k2:
    st.metric("BTC Dominance", f"{btc_dom:.1f}%", "share of universe market cap")
with k3:
    st.metric("7d Breadth", breadth, "coins with positive 7d return")
with k4:
    r30 = latest["price_change_percentage_30d_in_currency"].dropna()
    spread = r30.max() - r30.min() if len(r30) else 0
    st.metric("30d Return Spread", f"{spread:.1f}pp", f"best {r30.max():.1f}% · worst {r30.min():.1f}%")

divider()

# ── SECTION 1: CAPITAL FLOWS ──────────────────────────────────────────────────
section_label("01 · Where is capital flowing?")
col1, col2 = st.columns([2, 1])

with col1:
    top10 = latest.nlargest(10, "market_cap")["id"].tolist()
    flow_df = df[df["id"].isin(top10)].copy()

    fig = px.area(
        flow_df,
        x="date",
        y="market_cap_b",
        color="name",
        color_discrete_sequence=SEQUENTIAL_PALETTE,
    )
    fig.update_traces(line=dict(width=CHART["thin_line_width"]))
    style_chart(fig, title="Market Cap Over Time · Top 10 Coins (USD Billions)", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    dom_df = latest.nlargest(5, "market_cap")[["name", "market_cap_b"]].copy()
    others = latest.nsmallest(max(len(latest) - 5, 0), "market_cap")["market_cap"].sum() / 1e9
    dom_df = pd.concat(
        [dom_df, pd.DataFrame([{"name": f"Others ({max(len(latest) - 5, 0)})", "market_cap_b": others}])],
        ignore_index=True,
    )

    fig2 = go.Figure(
        go.Pie(
            labels=dom_df["name"],
            values=dom_df["market_cap_b"],
            hole=0.6,
            marker=dict(colors=SEQUENTIAL_PALETTE[: len(dom_df)], line=dict(color=COLORS["page_bg"], width=2)),
            textfont=dict(family=FONTS["mono_stack"], size=FONTS["chart_size"]),
        )
    )
    style_chart(fig2, title="Market Cap Concentration", showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)


divider()

# ── SECTION 2: LEADERS & LAGGARDS ────────────────────────────────────────────
section_label("02 · Which coins are leading and lagging?")
tab1, tab2, tab3 = st.tabs(["1 DAY", "7 DAYS", "30 DAYS"])


def performance_table(horizon_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    perf = latest[["name", "symbol", "current_price", "market_cap_b", horizon_col]].dropna()
    perf = perf.rename(
        columns={
            horizon_col: "return_%",
            "market_cap_b": "mcap_$B",
            "current_price": "price_$",
        }
    )
    perf["return_%"] = perf["return_%"].round(2)
    perf["price_$"] = perf["price_$"].round(4)
    perf["mcap_$B"] = perf["mcap_$B"].round(2)
    top = perf.nlargest(5, "return_%")[["name", "symbol", "price_$", "mcap_$B", "return_%"]]
    bottom = perf.nsmallest(5, "return_%")[["name", "symbol", "price_$", "mcap_$B", "return_%"]]
    return top, bottom


for tab, col in zip(
    [tab1, tab2, tab3],
    [
        "price_change_percentage_24h_in_currency",
        "price_change_percentage_7d_in_currency",
        "price_change_percentage_30d_in_currency",
    ],
):
    with tab:
        top5, bot5 = performance_table(col)
        c1, c2 = st.columns(2)
        with c1:
            sub_label("Top 5", tone="positive")
            st.table(style_table(top5.reset_index(drop=True)))

        with c2:
            sub_label("Bottom 5", tone="negative")
            st.table(style_table(bot5.reset_index(drop=True)))


divider()

# ── SECTION 3: MOMENTUM ───────────────────────────────────────────────────────
section_label("03 · What does momentum look like?")

mom = latest[
    [
        "name",
        "symbol",
        "price_change_percentage_24h_in_currency",
        "price_change_percentage_7d_in_currency",
        "price_change_percentage_30d_in_currency",
    ]
].dropna()
mom.columns = ["name", "symbol", "1d", "7d", "30d"]
mom["consistent_bull"] = (mom["1d"] > 0) & (mom["7d"] > 0) & (mom["30d"] > 0)
mom["consistent_bear"] = (mom["1d"] < 0) & (mom["7d"] < 0) & (mom["30d"] < 0)

col5, col6 = st.columns(2)

with col5:
    bulls = mom[mom["consistent_bull"]].sort_values("30d", ascending=False)
    sub_label("Consistent Bulls · Positive Across All Horizons", tone="positive")
    if len(bulls) > 0:
        fig5 = px.bar(
            bulls,
            x="name",
            y=["1d", "7d", "30d"],
            barmode="group",
            color_discrete_map=RETURN_COLORS,
        )
        style_chart(fig5, title=" ", showlegend=True)
        fig5.update_xaxes(tickangle=0, tickfont_size=FONTS["chart_size"] - 1)
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No coins positive across all three horizons today.")

with col6:
    bears = mom[mom["consistent_bear"]].sort_values("30d")
    sub_label("Consistent Bears · Negative Across All Horizons", tone="negative")
    if len(bears) > 0:
        fig6 = px.bar(
            bears,
            x="name",
            y=["1d", "7d", "30d"],
            barmode="group",
            color_discrete_map=NEGATIVE_RETURN_COLORS,
        )
        style_chart(fig6, title=" ", showlegend=True)
        fig6.update_xaxes(tickangle=0, tickfont_size=FONTS["chart_size"] - 1)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No coins negative across all three horizons today.")


divider()

# ── SECTION 4: COIN EXPLORER ──────────────────────────────────────────────────
section_label("04 · Coin Explorer")

coin_options = sorted(df["name"].unique().tolist())
selected_coin = st.selectbox(
    "Select a coin",
    coin_options,
    index=coin_options.index("Bitcoin") if "Bitcoin" in coin_options else 0,
)

coin_df = df[df["name"] == selected_coin].sort_values("date")
coin_latest = coin_df.iloc[-1]

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Current Price", f"${coin_latest['current_price']:,.4f}")
with m2:
    st.metric("Market Cap", f"${coin_latest['market_cap'] / 1e9:.2f}B")
with m3:
    st.metric("24h Return", f"{coin_latest['price_change_percentage_24h_in_currency']:.2f}%")
with m4:
    st.metric("30d Return", f"{coin_latest['price_change_percentage_30d_in_currency']:.2f}%")

fig7 = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    row_heights=[0.65, 0.35],
    vertical_spacing=0.04,
)

fig7.add_trace(
    go.Scatter(
        x=coin_df["date"],
        y=coin_df["current_price"],
        name="Price",
        line=dict(color=COLORS["accent"], width=CHART["line_width"]),
        fill="tozeroy",
        fillcolor=rgba(COLORS["accent"], CHART["fill_alpha_light"]),
    ),
    row=1,
    col=1,
)

fig7.add_trace(
    go.Bar(
        x=coin_df["date"],
        y=coin_df["total_volume_b"],
        name="Volume ($B)",
        marker_color=rgba(COLORS["accent"], CHART["bar_alpha"]),
    ),
    row=2,
    col=1,
)

style_chart(fig7, title=f"{selected_coin} · Price & Volume History", showlegend=False)
fig7.update_yaxes(gridcolor=COLORS["border"], linecolor=COLORS["border"])
fig7.update_xaxes(gridcolor=COLORS["border"], linecolor=COLORS["border"])
st.plotly_chart(fig7, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="border-top:1px solid {COLORS['border']}; margin-top:3rem; padding-top:1rem;">
      <p style="font-family:{FONTS['mono_stack']}; font-size:0.65rem; color:{COLORS['muted']}; letter-spacing:0.08em; text-transform:uppercase;">
        Data source: CoinGecko API · Universe fixed 2025-12-01 ·
        Updated daily via GitHub Actions ·
        Built by Milcah M. Joseph
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)
