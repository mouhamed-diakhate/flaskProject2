from flask import Flask, render_template
import geopandas as gpd
import pandas as pd
import pymongo
from bokeh.plotting import figure, output_file, save
from bokeh.models import GeoJSONDataSource, NumeralTickFormatter, HoverTool
from bokeh.palettes import Cividis
from bokeh.transform import linear_cmap

app = Flask(__name__)
def interpolate_color(color1, color2, n):
    colors = []
    for i in range(n):
        r = int(color1[0] + (color2[0] - color1[0]) * i / (n-1))
        g = int(color1[1] + (color2[1] - color1[1]) * i / (n-1))
        b = int(color1[2] + (color2[2] - color1[2]) * i / (n-1))
        colors.append((r, g, b))
    return colors
# Palette allant du vert au jaune
vert = (0, 255, 0)
jaune = (255, 255, 0)
palette_vert_jaune = interpolate_color(vert, jaune, 128)

# Palette allant du jaune au rouge
rouge = (255, 0, 0)
palette_jaune_rouge = interpolate_color(jaune, rouge, 128)

# Palette allant du vert au jaune au rouge
palette_vert_jaune_rouge = interpolate_color(vert, jaune, 64) + interpolate_color(jaune, rouge, 64)

@app.route('/ous')
def ousm():
    # Importer les données GeoJSON
    data = gpd.read_file('export.geojson')

    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["proj"]
    collection = db["pfc"]

    # Récupérer les données MongoDB
    data1 = list(collection.find())
    df = pd.DataFrame(data1)
    df.drop('_id', axis=1, inplace=True)
    df_fusionne = df.groupby('Région').sum(numeric_only=True).reset_index()

    # Fusionner les données
    data = data.merge(df_fusionne, left_on='name:frr', right_on='Région', how='left')

    # Créer la GeoJSONDataSource
    geo_source = GeoJSONDataSource(geojson=data.to_json())

    TOOLTIPS = [
        ("State", "@name:frr"),
        ("# Nombre de vote", "@{Ousmane SONKO}{(0,0)}"),
    ]

    # Configurer la figure Bokeh
    map_plot = figure(
        height=200,
        width=300,
        sizing_mode="scale_width",
        tooltips=TOOLTIPS,
        title="Résultats des élections présidentielles de 2019",
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
    )
    map_plot.grid.grid_line_color = None

    # Dessiner les polygones des états
    # sen = map_plot.patches(
    #     xs="xs",
    #     ys="ys",
    #     fill_color=linear_cmap(field_name="Ousmane SONKO", palette=Cividis[256], low=data["Ousmane SONKO"].min(),
    #                            high=data["Ousmane SONKO"].max()),
    #     source=geo_source,
    #     line_color="darkgrey",
    #     line_width=1,
    # )
    sen = map_plot.patches(
        xs="xs",
        ys="ys",
        fill_color=linear_cmap(
            field_name="Ousmane SONKO",
            palette=palette_vert_jaune_rouge,
            low=data["Ousmane SONKO"].min(),
            high=data["Ousmane SONKO"].max(),
        ),
        source=geo_source,
        line_color="darkgrey",
        line_width=1,
    )

    # Ajouter la barre de couleur
    color_bar = sen.construct_color_bar(formatter=NumeralTickFormatter(format="0,0"), height=10)
    map_plot.add_layout(obj=color_bar, place="below")

    # Sauvegarder le graphique Bokeh dans un fichier HTML temporaire
    output_file("templates/map_ous.html")
    save(map_plot)

    return render_template("ous.html")

@app.route('/cand')
def candidat():

    return  render_template('candidat.html')


@app.route('/carte')
def carte():
    # Importer les données GeoJSON
    data = gpd.read_file('export.geojson')

    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["proj"]
    collection = db["pfc"]

    # Récupérer les données MongoDB
    data1 = list(collection.find())
    df = pd.DataFrame(data1)
    df.drop('_id', axis=1, inplace=True)
    df_fusionne = df.groupby('Région').sum(numeric_only=True).reset_index()

    # Fusionner les données
    data = data.merge(df_fusionne, left_on='name:frr', right_on='Région', how='left')

    # Créer la GeoJSONDataSource
    geo_source = GeoJSONDataSource(geojson=data.to_json())

    # Configurer les infobulles
    TOOLTIPS = [
        ("Région", "@name:frr"),
    ]
    # Configurer la figure Bokeh
    map_plot = figure(
        height=200,
        width=300,
        sizing_mode="scale_width",
        tooltips=TOOLTIPS,
        title="Carte électorale",
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
    )
    map_plot.grid.grid_line_color = None

    # Dessiner les polygones des états
    # sen = map_plot.patches(
    #     xs="xs",
    #     ys="ys",
    #     fill_color=linear_cmap(field_name="Ousmane SONKO", palette=Cividis[256], low=data["Ousmane SONKO"].min(),
    #                            high=data["Ousmane SONKO"].max()),
    #     source=geo_source,
    #     line_color="darkgrey",
    #     line_width=1,
    # )
    sen = map_plot.patches(
        xs="xs",
        ys="ys",
        fill_color="green",  # couleur de fond
        line_color="darkgrey",
        line_width=1,
        hover_fill_color="red",  # couleur de survol
        source=geo_source,
    )

    # Ajouter un outil Hover pour afficher le nom de la région au survol
    hover = HoverTool()

    hover.tooltips = [
        ("Région", "@name:frr"),
    ]

    map_plot.add_tools(hover)


    # Sauvegarder le graphique Bokeh dans un fichier HTML temporaire
    output_file("templates/map_ous.html")
    save(map_plot)

    return render_template("carte.html")

@app.route('/as')
def ag():
    return render_template('a.html')


@app.route('/')
def home():
    return  render_template('acceuil.html')

@app.route('/ms')
def index():
    # Importer les données GeoJSON
    data = gpd.read_file('export.geojson')

    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["proj"]
    collection = db["pfc"]

    # Récupérer les données MongoDB
    data1 = list(collection.find())
    df = pd.DataFrame(data1)
    df.drop('_id', axis=1, inplace=True)
    df_fusionne = df.groupby('Région').sum(numeric_only=True).reset_index()

    # Fusionner les données
    data = data.merge(df_fusionne, left_on='name:frr', right_on='Région', how='left')

    # Créer la GeoJSONDataSource
    geo_source = GeoJSONDataSource(geojson=data.to_json())

    TOOLTIPS = [
        ("State", "@name:frr"),
        ("# Nombre de vote", "@{Macky SALL}{(0,0)}"),
    ]

    # Configurer la figure Bokeh
    map_plot = figure(
        height=200,
        width=300,
        sizing_mode="scale_width",
        tooltips=TOOLTIPS,
        title="Résultats des élections présidentielles de 2019",
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
    )
    map_plot.grid.grid_line_color = None

    # Dessiner les polygones des états
    # sen = map_plot.patches(
    #     xs="xs",
    #     ys="ys",
    #     fill_color=linear_cmap(field_name="Macky SALL", palette=Cividis[256], low=data["Macky SALL"].min(),
    #                            high=data["Macky SALL"].max()),
    #     source=geo_source,
    #     line_color="darkgrey",
    #     line_width=1,
    # )
    sen = map_plot.patches(
        xs="xs",
        ys="ys",
        fill_color=linear_cmap(
            field_name="Macky SALL",
            palette=palette_vert_jaune_rouge,
            low=data["Macky SALL"].min(),
            high=data["Macky SALL"].max(),
        ),
        source=geo_source,
        line_color="darkgrey",
        line_width=1,
    )

    # Ajouter la barre de couleur
    color_bar = sen.construct_color_bar(formatter=NumeralTickFormatter(format="0,0"), height=10)
    map_plot.add_layout(obj=color_bar, place="below")

    # Sauvegarder le graphique Bokeh dans un fichier HTML temporaire
    output_file("templates/map.html")
    save(map_plot)

    # Renvoyer le template HTML
    return render_template("index.html")


@app.route('/idy')
def idyr():
    # Importer les données GeoJSON
    data = gpd.read_file('export.geojson')

    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["proj"]
    collection = db["pfc"]

    # Récupérer les données MongoDB
    data1 = list(collection.find())
    df = pd.DataFrame(data1)
    df.drop('_id', axis=1, inplace=True)
    df_fusionne = df.groupby('Région').sum(numeric_only=True).reset_index()

    # Fusionner les données
    data = data.merge(df_fusionne, left_on='name:frr', right_on='Région', how='left')

    # Créer la GeoJSONDataSource
    geo_source = GeoJSONDataSource(geojson=data.to_json())

    TOOLTIPS = [
        ("State", "@name:frr"),
        ("# Nombre de vote", "@{Idrissa SECK}{(0,0)}"),
    ]

    # Configurer la figure Bokeh
    map_plot = figure(
        height=200,
        width=300,
        sizing_mode="scale_width",
        tooltips=TOOLTIPS,
        title="Résultats des élections présidentielles de 2019",
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
    )
    map_plot.grid.grid_line_color = None

    # Dessiner les polygones des états
    # sen = map_plot.patches(
    #     xs="xs",
    #     ys="ys",
    #     fill_color=linear_cmap(field_name="Idrissa SECK", palette=Cividis[256], low=data["Idrissa SECK"].min(),
    #                            high=data["Idrissa SECK"].max()),
    #     source=geo_source,
    #     line_color="darkgrey",
    #     line_width=1,
    # )
    #

    sen = map_plot.patches(
        xs="xs",
        ys="ys",
        fill_color=linear_cmap(
            field_name="Idrissa SECK",
            palette=palette_vert_jaune_rouge,
            low=data["Idrissa SECK"].min(),
            high=data["Idrissa SECK"].max(),
        ),
        source=geo_source,
        line_color="darkgrey",
        line_width=1,
    )

    # Ajouter la barre de couleur
    color_bar = sen.construct_color_bar(formatter=NumeralTickFormatter(format="0,0"), height=10)
    map_plot.add_layout(obj=color_bar, place="below")

    # Sauvegarder le graphique Bokeh dans un fichier HTML temporaire
    output_file("templates/map_idy.html")
    save(map_plot)

    return render_template("idy.html")

@app.route('/mad')
def madi():
    # Importer les données GeoJSON
    data = gpd.read_file('export.geojson')

    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["proj"]
    collection = db["pfc"]

    # Récupérer les données MongoDB
    data1 = list(collection.find())
    df = pd.DataFrame(data1)
    df.drop('_id', axis=1, inplace=True)
    df_fusionne = df.groupby('Région').sum(numeric_only=True).reset_index()

    # Fusionner les données
    data = data.merge(df_fusionne, left_on='name:frr', right_on='Région', how='left')

    # Créer la GeoJSONDataSource
    geo_source = GeoJSONDataSource(geojson=data.to_json())

    TOOLTIPS = [
        ("State", "@name:frr"),
        ("# Nombre de vote", "@{Madické NIANG}{(0,0)}"),
    ]

    # Configurer la figure Bokeh
    map_plot = figure(
        height=200,
        width=300,
        sizing_mode="scale_width",
        tooltips=TOOLTIPS,
        title="Résultats des élections présidentielles de 2019",
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
    )
    map_plot.grid.grid_line_color = None

    # Dessiner les polygones des états
    # sen = map_plot.patches(
    #     xs="xs",
    #     ys="ys",
    #     fill_color=linear_cmap(field_name="Madické NIANG", palette=Cividis[256], low=data["Madické NIANG"].min(),
    #                            high=data["Madické NIANG"].max()),
    #     source=geo_source,
    #     line_color="darkgrey",
    #     line_width=1,
    # )
    sen = map_plot.patches(
        xs="xs",
        ys="ys",
        fill_color=linear_cmap(
            field_name="Madické NIANG",
            palette=palette_vert_jaune_rouge,
            low=data["Madické NIANG"].min(),
            high=data["Madické NIANG"].max(),
        ),
        source=geo_source,
        line_color="darkgrey",
        line_width=1,
    )

    # Ajouter la barre de couleur
    color_bar = sen.construct_color_bar(formatter=NumeralTickFormatter(format="0,0"), height=10)
    map_plot.add_layout(obj=color_bar, place="below")

    # Sauvegarder le graphique Bokeh dans un fichier HTML temporaire
    output_file("templates/map_mad.html")
    save(map_plot)

    return render_template("mad.html")

@app.route('/ehj')
def ehja():
    # Importer les données GeoJSON
    data = gpd.read_file('export.geojson')

    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["proj"]
    collection = db["pfc"]

    # Récupérer les données MongoDB
    data1 = list(collection.find())
    df = pd.DataFrame(data1)
    df.drop('_id', axis=1, inplace=True)
    df_fusionne = df.groupby('Région').sum(numeric_only=True).reset_index()

    # Fusionner les données
    data = data.merge(df_fusionne, left_on='name:frr', right_on='Région', how='left')

    # Créer la GeoJSONDataSource
    geo_source = GeoJSONDataSource(geojson=data.to_json())

    TOOLTIPS = [
        ("State", "@name:frr"),
        ("# Nombre de vote", "@{El hadji SALL}{(0,0)}"),
    ]

    # Configurer la figure Bokeh
    map_plot = figure(
        height=200,
        width=300,
        sizing_mode="scale_width",
        tooltips=TOOLTIPS,
        title="Résultats des élections présidentielles de 2019",
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
    )
    map_plot.grid.grid_line_color = None

    # Dessiner les polygones des états
    # sen = map_plot.patches(
    #     xs="xs",
    #     ys="ys",
    #     fill_color=linear_cmap(field_name="El hadji SALL", palette=Cividis[256], low=data["El hadji SALL"].min(),
    #                            high=data["El hadji SALL"].max()),
    #     source=geo_source,
    #     line_color="darkgrey",
    #     line_width=1,
    # )
    sen = map_plot.patches(
        xs="xs",
        ys="ys",
        fill_color=linear_cmap(
            field_name="El hadji SALL",
            palette=palette_vert_jaune_rouge,
            low=data["El hadji SALL"].min(),
            high=data["El hadji SALL"].max(),
        ),
        source=geo_source,
        line_color="darkgrey",
        line_width=1,
    )

    # Ajouter la barre de couleur
    color_bar = sen.construct_color_bar(formatter=NumeralTickFormatter(format="0,0"), height=10)
    map_plot.add_layout(obj=color_bar, place="below")

    # Sauvegarder le graphique Bokeh dans un fichier HTML temporaire
    output_file("templates/map_ehl.html")
    save(map_plot)

    return render_template("ehj.html")

if __name__ == '__main__':
    app.run(debug=True)
