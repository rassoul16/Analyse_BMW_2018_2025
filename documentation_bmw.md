
Dans ce projet, nous analysons les ventes mondiales de BMW entre 2018 et 2025 afin de comprendre les performances commercialees et  l’évolution du marché automobile



Le tableau contient :

Year / Month → période de vente

Region → zone géographique

Model → type de voiture( les modeles premium sont : 5 Series, X5, X7, i4 , ix ;

les modeles electriques sont : i4, ix ;
les modeles qui sont ni premium , ni electrique : 3 Series , MINI  )

Ventes → nombre de voitures vendues

Prix_Moyen → prix moyen de vente

Chiffre_Affaires → revenu total

Part_Electrique → proportion de voitures électriques ,ainsi il est compris entre 0 et 1 .

C'est le pourcentage du nombre de voitures electriques vendues par rapport aux ventes totales  

Part_Premium → part des voitures haut de gamme .

c'est la part des voitures premiums vendues par rapport aux ventes totales.

Croissance_PIB → croissance économique ou richesse d'un pays

Indice_Carburant → évolution du prix du carburant ( 1 pour prix normal , 1.20 augmentation de 20%, 0.90 diminution de 10%"""






data.info()

 Nous pouvons voir clairement qu'il ya pas de valeurs manquantes


data.describe()

L’analyse descriptive montre que dataset est complet mais avec certaines valeurs incohérentes, notamment dans la part électrique.
nous voyons des valeurs négatives alors que la variable est une proportion et doit etre compris entre 0 et 1


col_num = data.select_dtypes(include=[np.number]).columns

for col in col_num:
    fig = px.box(data, y=col, title=f"Boxplot de {col}")
    fig.show()

"""L’analyse des boxplots montre la présence de valeurs aberrantes dans certaines variables comme les ventes et le chiffre d’affaires. Ces valeurs sont cohérentes avec le contexte économique et représentent des observations réelles"""

#là on supprime les valeurs negatifs
data = data[data["BEV_Share"] >= 0]

"""La suppression des valeurs négatives de BEV_Share permet d’améliorer la qualité des données et d’obtenir des résultats plus fiables, car cette variable représente une proportion qui ne peut pas être négative"""

#correlation et heatmap
correlation = data.select_dtypes(include=[np.number]).corr()
fig = px.imshow(correlation,text_auto=True,color_continuous_scale='RdBu_r',
    title='Correlation Heatmap BMW')
fig.show()

"""1. Ventes ↔ Chiffre d’affaires (≈ 0.86)

Très forte corrélation positive

quand les ventes augmentent, le revenu augmente

Le chiffre d’affaires dépend directement du volume des ventes

2. Part_Electrique ↔ Year (≈ 0.98)

Corrélation très forte

plus le temps passe, plus de voitures électriques

On observe une forte progression des véhicules électriques au fil des années

3. Part_Electrique ↔ Indice_Carburant (≈ 0.95)

Corrélation forte

plus le prix du carburant augmente, plus les voitures électriques augmentent ↑

4. Prix_Moyen ↔ Chiffre d’affaires (≈ 0.5)

Corrélation modérée

le prix influence le revenu



5. Croissance_PIB ↔ Ventes (≈ 0)

Corrélation faible

peu d’impact

La croissance économique a un impact limité sur les ventes BMW.

6. Part_Premium ↔ autres variables

Corrélation faible

La part premium reste stable et indépendante des autres facteurs.

7. Month ↔ toutes les variables

corr ≈ 0

Les ventes ne présentent pas de variation saisonnière significative.
"""

#visualiser la relation en utilisant px.scatter
px.scatter(data, x="Ventes", y="Chiffre_Affaires",color="Chiffre_Affaires")

"""Le nuage de points montre une relation positive forte entre les ventes et le chiffre d’affaires. Les points suivent une tendance linéaire ascendante, indiquant que l’augmentation du volume des ventes entraîne une hausse du revenu

# Baisse des voitures premium
la baisse des voitures premium s'explique par la transition vers les voitures electriques.

les modeles premium sont : 5 Series, X5, X7

les modeles electriques sont : i4, ix

# **CONCLUSION**

L’analyse montre que BMW dépend principalement du volume des ventes. La transition vers les véhicules électriques est en forte progression, tandis que les facteurs économiques ont un impact limité
"""