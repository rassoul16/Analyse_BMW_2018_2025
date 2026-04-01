import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import seaborn as sns
from scipy.stats import pearsonr

# ===============================
# Chargement des données
# ===============================
data = pd.read_csv("bmw_global_sales_2018_2025.csv")

# ===============================
# Renommer les variables
# ===============================
data = data.rename(columns={
    "Units_Sold": "Ventes",
    "Avg_Price_EUR": "Prix_Moyen",
    "Revenue_EUR": "Chiffre_Affaires",
    "BEV_Share": "Part_Electrique",
    "Premium_Share": "Part_Premium",
    "GDP_Growth": "Croissance_PIB",
    "Fuel_Price_Index": "Indice_Carburant"
})

# ===============================
# Exploration des données
# ===============================
print(data.head(10))
data.info()
data.describe()

# ===============================
# Valeurs manquantes
# ===============================
print(data.isnull().sum())

# ===============================
# Boxplots des variables numériques
# ===============================
col_num = data.select_dtypes(include=[np.number]).columns

for col in col_num:
    fig = px.box(data, y=col, title=f"Boxplot de {col}")
    fig.show()

# ===============================
# Détection des outliers (IQR)
# ===============================
for col in col_num:
    Q1 = np.percentile(data[col], 25)
    Q3 = np.percentile(data[col], 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)]

    print(f"{col}: lower bound = {lower_bound}, upper bound = {upper_bound}")

# ===============================
# Nettoyage données
# ===============================

# Valeurs électriques négatives
data[data["Part_Electrique"] < 0]

# Valeurs électriques > 1
data[data["Part_Electrique"] > 1]

# Suppression des valeurs négatives
data = data[data["Part_Electrique"] >= 0]

print(len(data))

# ===============================
# Visualisations
# ===============================

# Boxplot ventes par région
fig = px.box(data, x="Region", y="Ventes", color="Region",
             title="Distribution des ventes par région")
fig.show()

# Boxplot CA par modèle
fig = px.box(data, x="Model", y="Chiffre_Affaires", color="Model",
             title="Distribution du revenu par modèle")
fig.show()

# Boxplot électrique par région
fig = px.box(data, x="Region", y="Part_Electrique", color="Region",
             title="Distribution des parts électriques par région")
fig.show()

# Boxplot premium par région
fig = px.box(data, x="Region", y="Part_Premium", color="Region",
             title="Distribution du segment premium par région")
fig.show()

# ===============================
# Corrélation
# ===============================
correlation = data.select_dtypes(include=[np.number]).corr()

fig = px.imshow(correlation,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                title='Correlation Heatmap BMW')
fig.show()

# ===============================
# Suppression colonne inutile
# ===============================
data = data.drop("Month", axis=1)

# ===============================
# Relation ventes vs CA
# ===============================
px.scatter(data,
           x="Ventes",
           y="Chiffre_Affaires",
           color="Chiffre_Affaires")

# ===============================
# Analyse temporelle
# ===============================

# Evolution des ventes
sales = data.groupby("Year")["Ventes"].sum().reset_index()

px.line(sales,
        x="Year",
        y="Ventes",
        title="Evolution des ventes BMW")

# Evolution du chiffre d'affaires
revenue = data.groupby("Year")["Chiffre_Affaires"].sum().reset_index()

px.line(revenue,
        x="Year",
        y="Chiffre_Affaires",
        title="Evolution du chiffre d'affaires")

# Evolution véhicules électriques
bev = data.groupby("Year")["Part_Electrique"].mean().reset_index()

px.line(bev,
        x="Year",
        y="Part_Electrique",
        title="Evolution des véhicules électriques")

# Evolution premium
premium = data.groupby("Year")["Part_Premium"].mean().reset_index()

px.line(premium,
        x="Year",
        y="Part_Premium",
        title="Evolution du segment premium")

# ===============================
# Analyse par région
# ===============================

# Moyennes
print(data.groupby("Region")[["Ventes", "Chiffre_Affaires"]].mean())

# CA total par région
region_revenue = data.groupby("Region")["Chiffre_Affaires"].sum().reset_index()

px.bar(region_revenue,
       x="Region",
       y="Chiffre_Affaires",
       title="Chiffre d'affaires par région")

# Moyenne ventes + électrique
print(data.groupby("Region")[["Ventes", "Part_Electrique"]].mean())

# Part électrique par région
region_bev = data.groupby("Region")["Part_Electrique"].mean().reset_index()

px.bar(region_bev,
       x="Region",
       y="Part_Electrique",
       title="Part électrique par région")