import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="BMW Sales", layout="wide")

# ── STYLE ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d0d0d; color: #f0f0f0; }
    section[data-testid="stSidebar"] { background-color: #141414; }
    h1, h2, h3 { color: #1a6fc4 !important; }
    [data-testid="stMetric"] {
        background: #1a1a1a; border: 1px solid #2a2a2a;
        border-radius: 10px; padding: 12px;
    }
    [data-testid="stMetricLabel"] { color: #888 !important; }
    [data-testid="stMetricValue"] { color: #fff !important; }
    .alert { padding: 10px 14px; border-radius: 8px; margin: 6px 0; font-size: 13px; }
    .info    { background:#0c2340; border-left:4px solid #1a6fc4; color:#90caf9; }
    .success { background:#0a2018; border-left:4px solid #2e7d32; color:#a5d6a7; }
    .warning { background:#2a1a06; border-left:4px solid #f57c00; color:#ffcc80; }
</style>
""", unsafe_allow_html=True)

def alert(msg, kind="info"):
    st.markdown(f'<div class="alert {kind}">  {msg}</div>', unsafe_allow_html=True)

def dark(fig):
    # applique le fond transparent et les couleurs sombres à tous les graphiques
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f0f0f0"),
        xaxis=dict(gridcolor="#222"), yaxis=dict(gridcolor="#222"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

# ── CHARGEMENT DES DONNÉES ─────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("bmw_global_sales_2018_2025.csv")
    df["Revenue_per_unit"] = df["Revenue_EUR"] / df["Units_Sold"]
    return df

data = load()

# ── SIDEBAR : FILTRES ──────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/80px-BMW.svg.png", width=55)
st.sidebar.markdown("### Filtres")

years   = st.sidebar.multiselect("Années",  sorted(data["Year"].unique()),   default=sorted(data["Year"].unique()))
regions = st.sidebar.multiselect("Régions", sorted(data["Region"].unique()), default=sorted(data["Region"].unique()))
models  = st.sidebar.multiselect("Modèles", sorted(data["Model"].unique()),  default=sorted(data["Model"].unique()))

# on filtre le dataframe principal selon les sélections de la sidebar
df = data[
    data["Year"].isin(years) &
    data["Region"].isin(regions) &
    data["Model"].isin(models)
].copy()

if df.empty:
    alert("Aucune donnée pour ces filtres.", "warning")
    st.stop()

# ── TITRE ──────────────────────────────────────────────────────────────────────
st.title("🚗 BMW Global Sales Dashboard")

# ── ALERTES ────────────────────────────────────────────────────────────────────
# alertes automatiques basées sur les données filtrées
st.subheader("Alertes")

bev_last = df[df["Year"] == df["Year"].max()]["BEV_Share"].mean()
bev_prev = df[df["Year"] == df["Year"].max() - 1]["BEV_Share"].mean()
if bev_last > bev_prev:
    alert(f"Part électrique en hausse : {bev_last:.1%} vs {bev_prev:.1%} l'an dernier.", "success")
else:
    alert(f"Part électrique en baisse : {bev_last:.1%} vs {bev_prev:.1%} l'an dernier.", "warning")

if "RestOfWorld" in df["Region"].values:
    if df[df["Region"] != "RestOfWorld"]["Premium_Share"].mean() > df[df["Region"] == "RestOfWorld"]["Premium_Share"].mean():
        alert("Les ventes premium sont plus élevées dans les autres régions qu'en Rest of World.", "info")

# ── KPIs ───────────────────────────────────────────────────────────────────────
st.subheader("Indicateurs clés")

# Q1 et Q3 calculés sur les données filtrées (recommandation prof)
q1  = df["Units_Sold"].quantile(0.25)
q3  = df["Units_Sold"].quantile(0.75)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("CA total",            f"{df['Revenue_EUR'].sum()/1e9:.1f} Md €")
c2.metric("Ventes totales",      f"{int(df['Units_Sold'].sum()):,}")
c3.metric("Part électrique",     f"{df['BEV_Share'].mean():.1%}")
c4.metric("Part premium",        f"{df['Premium_Share'].mean():.1%}")


st.info(f"ℹ️ 75% des lignes ont vendu **{int(q3):,} véhicules ou moins** (Q3)")

# ÉVOLUTION DES VENTES 
st.subheader("Évolution des ventes")

fig = px.line(
    df.groupby("Year")["Units_Sold"].sum().reset_index(),
    x="Year", y="Units_Sold", markers=True,
    color_discrete_sequence=["#1a6fc4"],
    labels={"Units_Sold": "Ventes", "Year": "Année"}
)
st.plotly_chart(dark(fig), use_container_width=True)

#  BOXPLOT VENTES PAR MODÈLE
# le boxplot est le meilleur graphique pour voir médiane, Q1/Q3 et outliers d'un coup
st.subheader("Distribution des ventes par modèle (Boxplot)")

fig = px.box(df, x="Model", y="Units_Sold", color="Model",
             color_discrete_sequence=px.colors.qualitative.Bold,
             points="outliers",
             labels={"Units_Sold": "Ventes", "Model": "Modèle"})
st.plotly_chart(dark(fig), use_container_width=True)

# HISTOGRAMME CA + TEST DE NORMALITÉ
# l'histogramme permet de voir si la distribution est normale ou asymétrique
st.subheader("Distribution du chiffre d'affaires")

col1, col2 = st.columns([2, 1])

with col1:
    region_sel = st.selectbox("Par région :", ["Toutes"] + sorted(df["Region"].unique().tolist()))
    df_h = df if region_sel == "Toutes" else df[df["Region"] == region_sel]
    fig = px.histogram(df_h, x="Revenue_EUR", nbins=50,
                       color_discrete_sequence=["#1a6fc4"],
                       labels={"Revenue_EUR": "CA (€)"})
    st.plotly_chart(dark(fig), use_container_width=True)

with col2:
    # test de Shapiro-Wilk pour vérifier la normalité (recommandation prof)
    st.markdown("#### Test de normalité (Shapiro-Wilk)")
    sample = df_h["Revenue_EUR"].sample(min(500, len(df_h)), random_state=42)
    _, p = stats.shapiro(sample)
    st.metric("p-value", f"{p:.5f}")
    if p < 0.05:
        alert("p < 0.05 → Distribution non normale → utilisez Spearman.", "warning")
    else:
        alert("p ≥ 0.05 → Distribution normale → vous pouvez utiliser Pearson.", "success")

# CORRÉLATION INTERACTIVE 
st.subheader("Analyse de corrélation")

num_vars = ["Units_Sold", "Revenue_EUR", "BEV_Share", "Premium_Share", "GDP_Growth", "Fuel_Price_Index"]

# deux listes séparées pour éviter que l'utilisateur choisisse deux fois la même variable
col_a, col_b = st.columns(2)
var1 = col_a.selectbox("Première variable", num_vars, index=0)
var2 = col_b.selectbox("Deuxième variable", [v for v in num_vars if v != var1], index=0)

if var1 and var2:
    # calcul de la corrélation de Spearman (ne nécessite pas de normalité, plus robuste)
    r, p_val = stats.spearmanr(df[var1], df[var2])

    fig = px.scatter(df, x=var1, y=var2, opacity=0.4, trendline="ols",
                     color_discrete_sequence=["#1a6fc4"])
    st.plotly_chart(dark(fig), use_container_width=True)

    col_r1, col_r2 = st.columns(2)
    col_r1.metric("Coefficient de corrélation (r)", f"{r:.3f}")
    col_r2.metric("p-value", f"{p_val:.5f}")

    # interprétation simple pour l'administration
    if p_val < 0.05:
        force = "forte" if abs(r) >= 0.7 else "modérée" if abs(r) >= 0.4 else "faible"
        sens  = "positive (augmentent ensemble)" if r > 0 else "négative (l'une augmente quand l'autre baisse)"
        alert(f"Relation {force} et {sens} entre {var1} et {var2}.", "success")
    else:
        alert(f"Pas de relation significative entre {var1} et {var2}.", "warning")

# RECOMMANDATIONS FINALES 
st.subheader("Recommandations")

top_ventes = df.groupby("Model")["Units_Sold"].sum().idxmax()
top_renta  = df.groupby("Model")["Revenue_per_unit"].mean().idxmax()
top_elec   = df.groupby("Model")["BEV_Share"].median().idxmax()

alert(f"Modèle le plus vendu : **{top_ventes}**", "success")
alert(f"Modèle le plus rentable (€/véhicule) : **{top_renta}**", "success")
alert(f"Meilleur positionnement électrique : **{top_elec}**", "info")

st.caption("BMW Global Sales · 2018–2025 ")