import json

from pathlib import Path
import branca
import folium
import requests
import streamlit as st
from streamlit_folium import st_folium


st.set_page_config(layout='wide')

m = folium.Map(location=[-23.519125 , -46.1852867],  zoom_start=30)


# Função para formatar o conteúdo do pop-up
tooltip = folium.GeoJsonTooltip(
    fields=["distrito", "pop_2010"],
    aliases=["Distrito: ", "População 2010: "],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 3px solid;
        border-color: black;
        border-radius: 3px;
        box-shadow: 5px;
    """,
    max_width=600,
)

url = ('D:/00-PMMC/CODATA - SMTDA/GEO BAIRROS E DISTRITOS PARA openstreetmap/regioes_plan.geojson')
geo = folium.GeoJson(url, name="regioes_plan", tooltip=tooltip).add_to(m)

# folium.Circle(
#     radius=500,
#     location=[-23.519125 , -46.1852867],
#     popup="CENTRO MOGI DAS CRUZES",
#     color="red",
#     fill=True,
#     fill_color='red',
# ).add_to(m)

folium.CircleMarker(
    location=[-23.519125 , -46.1852867],
    radius=5,
    popup="CENTRO MOGI DAS CRUZES",
    color="#3186cc",
    # color="red",
    fill=True,
    fill_color="#3186cc",
).add_to(m)


# # Função para lidar com o clique do mouse
# def on_map_click(e):
#     lat = e.latlng[0]
#     lon = e.latlng[1]
#     print(f"Coordenadas do clique: Latitude {lat}, Longitude {lon}")

# # Adicionando um evento de clique ao mapa
# m.add_child(folium.ClickForMarker(popup="Clique para adicionar um marcador"))
# m.add_child(folium.LatLngPopup())  # Exibe as coordenadas no canto inferior direito



st_data = st_folium(m, use_container_width=True)



# st.write(geo.data)