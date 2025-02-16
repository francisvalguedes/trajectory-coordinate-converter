import pandas as pd
import folium
# from streamlit_folium import st_folium
# from streamlit_js_eval import streamlit_js_eval
# import geojson
from folium import plugins
import geopandas as gpd
import streamlit as st
from lib.constants import  ConstantsNamespace
import json

cn = ConstantsNamespace()

def data_map_concat(df_p , df_s, df_s1 = pd.DataFrame()):
    if 'name' in df_p.columns: # Forçar a coluna 'name' a ser do tipo string         
        df_p['name'] = df_p['name'].astype(str)

    # Defina o tamanho máximo de pontos para a plotagem
    max_points = 100
    interval = max(len(df_p) // max_points, 1)

    # Se o número de pontos for maior que o limite, reamostrar
    if len(df_p) > max_points:
        # Sempre incluir o primeiro e o último ponto 
        first_point = df_p.iloc[0] 
        last_point = df_p.iloc[-1]
        df_p = df_p.iloc[::interval]
        df_p = pd.concat([pd.DataFrame([first_point]), df_p, pd.DataFrame([last_point])])
        st.info('Muitos dados para o mapa, selecionados o primeiro, o ultimo e mais ' + str(max_points) + ' pontos intermediários da série de dados', icon=cn.WARNING )

    df_s['sensor'] = 1
    if len(df_s1.index>0):
        df_s1['sensor'] = 1

    df = pd.concat([df_p, df_s, df_s1], axis=0).reset_index(drop=True)

    # Lista de cores predefinidas no Folium
    predefined_colors = {
    'blue': '#0000ff',
    'green': '#008000',
    'orange': '#ffa500',
    'red': '#ff0000',
    'purple': '#800080',
    'pink': '#ffc0cb',
    'darkred': '#8b0000',
    'lightred': '#f08080',
    'beige': '#f5f5dc',
    'darkblue': '#00008b',
    'darkgreen': '#006400',
    'cadetblue': '#5f9ea0',
    'lightblue': '#add8e6',
    'gray': '#808080',
    'black': '#000000',
    'lightgray': '#d3d3d3'
    }
    df['color'] = df.get('color', 'red')
    df['color'] = df['color'].apply(lambda x: x if x in predefined_colors else 'red')
    # Criar a nova coluna 'color_exadecimal' usando o dicionário
    df['color_ex'] = df['color'].map(predefined_colors)
    return df

# https://bikeshbade.com.np/tutorials/Detail/?title=Beginner+guide+to+python+Folium+module+to+integrate+google+earth+engine&code=8
def create_map2(df, gdf_imp= gpd.GeoDataFrame()):
    # Carregar a configuração da camada a partir do arquivo JSON com tratamento de exceção
    try:
        with open('config/map_tilelayer.json', 'r') as f:
            layer_config = json.load(f)
    except FileNotFoundError:
        st.warning("O arquivo 'config/map_tilelayer.json' não foi encontrado.", icon=cn.WARNING)
        layer_config = []
    except json.JSONDecodeError:
        st.warning("Falha ao decodificar o arquivo JSON.", icon=cn.WARNING)
        layer_config = []
    except:
        st.warning("Falha JSON.", icon=cn.WARNING)
        layer_config = []

    mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=8)
    # https://leaflet-extras.github.io/leaflet-providers/preview/
    # https://maps.stamen.com/terrain/#10/-5.92375/-35.16127
    
    # Adicione o tile layer ao mapa com tratamento de exceção
    for line in layer_config:
        try:
            folium.TileLayer(**line).add_to(mapa)
        except Exception as e:
            st.warning(f"Erro ao adicionar a camada: {e}", icon=cn.WARNING)

    # Adiciona marcadores como um grupo de camada
    camada_marcadores = folium.FeatureGroup(name="Marcadores", show=True)

    for  _, row in df.iterrows():
        icon = folium.Icon( color=row.get('color', "red") )
        popup = folium.Popup(row.get('name', ''), show=True, sticky=True)  # , sticky=True Popup exibido automaticamente
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=popup,
            tooltip=f"lat: {row['lat']:.5f}°, lon: {row['lon']:.5f}°, h: {row['height']:.2f} m",
            icon=icon,
        ).add_to(camada_marcadores)

    camada_marcadores.add_to(mapa)

    # Adiciona uma linha como um grupo de camada
    camada_linhas = folium.FeatureGroup(name="Linhas", show=True)

    df2 = df[df['sensor']!=1]
    linha = df2[['lat', 'lon']].values.tolist()

    folium.PolyLine(linha, color="blue", weight=2.5, opacity=1).add_to(camada_linhas)
    camada_linhas.add_to(mapa)

    if not gdf_imp.empty:
        camada_geo = folium.FeatureGroup(name="gaeo", show=True)
        folium.GeoJson(gdf_imp, name="GeoJSON").add_to(camada_geo)
        camada_geo.add_to(mapa)

    # Adiciona controle de camadas
    folium.LayerControl().add_to(mapa)

    #mouse position
    fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
    plugins.MousePosition(position='bottomright',
                        separator=' | ',
                        prefix="Mouse:",
                        lat_formatter=fmtr,
                        lng_formatter=fmtr).add_to(mapa)

    #Add measure tool
    mapa.add_child(plugins.MeasureControl(position='bottomright',
                                        primary_length_unit='meters',
                                        secondary_length_unit='miles',
                                        primary_area_unit='sqmeters',
                                        secondary_area_unit='acres').add_to(mapa))

    #fullscreen
    plugins.Fullscreen().add_to(mapa)

    #GPS
    plugins.LocateControl().add_to(mapa)

    #Add the draw 
    plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=None, edit_options=None).add_to(mapa)  
    return mapa

def create_map(df):
    # Criar o mapa com Folium
    mapa = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=10)
    for _, row in df.iterrows():
        icon = folium.Icon(
        color=row.get('color', "red")
        )
        marker = folium.Marker(
            location=[row['lat'], row['lon']],
            popup=row.get('name'),
            tooltip=f"lat: {row['lat']:.5f}°, lon: {row['lon']:.5f}°, h: {row['height']:.2f} m", #, wgs: {row.get('ellipsoid')}
            icon=icon
        ).add_to(mapa)
        marker.add_child(folium.Popup(row.get('name'), show=True))
    return mapa

# def add_geojson_line(mapa, df):
#     # Criar a geometria LineString
#     coordinates = [(row['lon'], row['lat']) for _, row in df.iterrows()]
#     line = geojson.LineString(coordinates)
#     # Criar uma Feature para a LineString
#     line_feature = geojson.Feature(geometry=line, properties={}) # properties pode ser um dicionário
#     # Criar o FeatureCollection combinando a LineString e os pontos
#     feature_collection = geojson.FeatureCollection([line_feature])
#     # popup = folium.GeoJsonPopup(fields=["name"],aliases=["height"])
#     folium.GeoJson(
#         feature_collection,
#         #popup=popup,
#     ).add_to(mapa)
#     return mapa