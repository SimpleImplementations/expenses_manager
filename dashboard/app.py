import pandas as pd
import plotly.express as px
import requests
import streamlit as st

TEMPLATE = "plotly_dark"

st.set_page_config(page_title="Money Manager", layout="wide")


@st.cache_data(ttl=60)
def load_expenses() -> pd.DataFrame:
    bot_url = st.secrets["bot_url"].rstrip("/")
    api_secret = st.secrets["api_secret"]
    resp = requests.get(f"{bot_url}/api/expenses", headers={"Authorization": f"Bearer {api_secret}"}, timeout=10)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


try:
    df = load_expenses()
except Exception as e:
    st.error(f"No se pudo conectar al bot: {e}")
    st.stop()

if df.empty:
    st.info("No hay gastos registrados aún.")
    st.stop()

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.title("Filtros")

users = sorted(df["user_id"].unique().tolist())
selected_user = st.sidebar.selectbox("Usuario (Telegram ID)", users)

min_date, max_date = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Período", value=(min_date, max_date), min_value=min_date, max_value=max_date)

currencies = ["Todas"] + sorted(df["currency"].unique().tolist())
selected_currency = st.sidebar.selectbox("Moneda", currencies)

if st.sidebar.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()

# Apply filters
filtered = df[df["user_id"] == selected_user]
if len(date_range) == 2:
    filtered = filtered[
        (filtered["date"].dt.date >= date_range[0]) &
        (filtered["date"].dt.date <= date_range[1])
    ]
if selected_currency != "Todas":
    filtered = filtered[filtered["currency"] == selected_currency]

# ── KPIs ───────────────────────────────────────────────────────────────────────
st.title("💸 Money Manager")

kpi_cols = st.columns(1 + len(filtered["currency"].unique()))
kpi_cols[0].metric("Transacciones", len(filtered))
for i, (cur, grp) in enumerate(filtered.groupby("currency"), start=1):
    kpi_cols[i].metric(f"Total {cur}", f"{grp['value'].sum():,.2f}")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Gastos por mes")
    monthly = filtered.groupby(["month", "currency"])["value"].sum().reset_index()
    fig = px.bar(monthly, x="month", y="value", color="currency",
                 barmode="group", template=TEMPLATE,
                 labels={"value": "Monto", "month": "Mes"})
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Por categoría")
    by_cat = filtered.groupby("category")["value"].sum().reset_index()
    fig = px.pie(by_cat, names="category", values="value", template=TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Categorías por mes")
cat_month = filtered.groupby(["month", "category"])["value"].sum().reset_index()
fig = px.bar(cat_month, x="month", y="value", color="category",
             barmode="stack", template=TEMPLATE,
             labels={"value": "Monto", "month": "Mes"})
st.plotly_chart(fig, use_container_width=True)

# ── Raw data ───────────────────────────────────────────────────────────────────
with st.expander("Ver todos los gastos"):
    st.dataframe(
        filtered[["date", "value", "currency", "category", "message"]]
        .sort_values("date", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
    )
