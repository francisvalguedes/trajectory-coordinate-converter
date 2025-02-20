import streamlit as st
import pandas as pd
import numpy as np
import pymap3d as pm
import re
import geopandas as gpd
from lib.constants import  ConstantsNamespace

cn = ConstantsNamespace()

@st.cache_data
def read_csv_index(file_path):
    # Lê o CSV sem atribuição de índice e apaga linhas vazias
    df = pd.read_csv(file_path).dropna(how='all')
    
    # Verifica se a primeira coluna não tem nome e é candidata a ser índice
    if df.columns[0] == 'Unnamed: 0':
        df.set_index(df.columns[0], inplace=True)
        df.index.name = None 
    return df

def data_concat(df1, df2):
    #verifica se tem colunas duplicadas
    duplicadas = df1.columns.intersection(df2.columns.tolist())
    # apaga as colunas duplicadas no df antigo 
    df1 = df1.drop(columns=duplicadas, axis=1)
    return pd.concat([df1, df2], axis=1) # retorna concatenado

def converter_unidades(df, mkm='m', radgraus='graus'):
    # Converter radianos para graus
    if radgraus == 'rad':
        for coluna in ['Az', 'El', 'lat', 'lon']:
            if coluna in df.columns:
                df[coluna] = np.degrees(df[coluna])
    
    # Converter quilômetros para metros
    if mkm == 'km':
        for coluna in ['r','x', 'y', 'z', 'X', 'Y', 'Z']:
            if coluna in df.columns:
                df[coluna] = df[coluna] * 1000
    
    return df


def upload_geojson():
    exp_file_map = st.expander("Entre com arquivo de mapa GeoJson salvo anteriormente:", expanded=False)
    geojson_in = exp_file_map.file_uploader("Carregue arquivo de mapa salvo - GeoJson", type='geojson')
    if geojson_in is not None:
        gdf_data = gpd_geojson_read(geojson_in)
    else: 
        gdf_data = gpd.GeoDataFrame()
    return gdf_data

def gpd_geojson_read(geojson_in):
    if geojson_in is not None:
        try:      
            gdf_data = gpd.read_file(geojson_in)
            st.info('Pontos carregados:', icon=cn.INFO)
        except:
            st.warning('arquivo não compatível', icon=cn.WARNING)
            st.stop()
    return gdf_data

#@st.cache_data
def pd_csv_read(caminho_csv):
    return pd.read_csv(caminho_csv).dropna(how='all')

def data_input_azelr():
    expander = st.expander("Entre com as coordenadas:", expanded=True)
    Azimute = expander.number_input('Azimute(graus)', 0.0, 360.0, format="%.6f", key='Azimute',  value= cn.GAMA_BRN_AZ ) 
    Elevação = expander.number_input('Elevação(graus)', -180.0, 180.0, format="%.6f", key='Elevação', value= cn.GAMA_BRN_EL)
    Range = expander.number_input('Range(m)', 0.0, 50000000.0, format="%.3f", key='Range',  value= cn.GAMA_BRN_D)
    return pd.DataFrame({"Az": [Azimute], "El": [Elevação], "r": [Range]})

def data_input_geodesicas():
    expander = st.expander("Entre com as coordenadas:", expanded=True)
    latitude = expander.number_input('Latitude(graus)', -90.0, 90.0, cn.GAMA_LAT, format="%.6f", key='Latitude')
    longitude = expander.number_input('Longitude(graus)', -180.0, 180.0, cn.GAMA_LON, format="%.6f", key='Longitude')
    height = expander.number_input('Altura (m)', -1000000.0, 50000000.0, cn.GAMA_H, format="%.2f", key='Altura')
    return pd.DataFrame({"name": ['Manual'], "lat": [latitude], "lon": [longitude], "height": [height]})

def data_input_enu():
    expander = st.expander("Entre com as coordenadas:", expanded=True)
    enu_x = expander.number_input('enu_x(m)', -50000000.0, 50000000.0, 0.0, format="%.3f", key='enu_x')
    enu_y = expander.number_input('enu_y(m)', -50000000.0, 50000000.0, 0.0, format="%.3f", key='enu_y')
    enu_z = expander.number_input('enu_z(m)', -50000000.0, 50000000.0, 0.0, format="%.3f", key='enu_z')
    return pd.DataFrame({"x": [enu_x], "y": [enu_y], "z": [enu_z]})

def data_input_ecef():
    expander = st.expander("Entre com as coordenadas:", expanded=True)
    x = expander.number_input('ECEF_X (metros)', -10000000.0, 10000000.0, cn.GAMA_ECEF_X, format="%.2f", key='ECEF_X')
    y = expander.number_input('ECEF_Y (metros)', -10000000.0, 10000000.0, cn.GAMA_ECEF_Y, format="%.2f", key='ECEF_Y')
    z = expander.number_input('ECEF_Z (metros)', -10000000.0, 10000000.0, cn.GAMA_ECEF_Z, format="%.2f", key='ECEF_Z')
    return pd.DataFrame({"ECEF_X": [x], "ECEF_Y": [y], "ECEF_Z": [z]})
    
def find_coord_ecef(df):
    """
    Ajusta e arquivo de configuração dos pontos de referência.
    """
    colunas_esperadas = ['ECEF_X', 'ECEF_Y', 'ECEF_Z']
    if not all(col in df.columns for col in colunas_esperadas):
        st.error("Verifique se as colunas obrigatórias (ECEF_X, ECEF_Y, ECEF_Z) estão presentes", icon=cn.ERROR)
        st.stop()
    if not all(df[col].dtype in ['float64', 'int64'] for col in colunas_esperadas):
        st.error("Verifique se o tipo de dado está correto", icon=cn.ERROR)
        st.stop()
    return df

def find_coord_geod(df):
    """
    Ajusta e arquivo de configuração dos pontos de referência.
    """
    colunas_esperadas = ['lat', 'lon', 'height']
    if not all(col in df.columns for col in colunas_esperadas):
        st.error("Verifique se as colunas obrigatórias estão presentes", icon=cn.ERROR)
        st.stop()
    if not all(df[col].dtype in ['float64', 'int64'] for col in colunas_esperadas):
        st.error("Verifique se o tipo de dado está correto", icon=cn.ERROR)
        st.stop()
    return df

def sensor_registration():
    # adicionar novo ponto de referência (sensor)    
    lc_expander = st.sidebar.expander("Adicionar novo ponto de referência no WGS84", expanded=False)
    lc_name = lc_expander.text_input('Nome', "minha localização")
    latitude = lc_expander.number_input('Latitude', -90.0, 90.0, 0.0, format="%.6f")
    longitude = lc_expander.number_input('Longitude', -180.0, 180.0, 0.0, format="%.6f")
    height = lc_expander.number_input('Altitude (m)', -1000.0, 2000.0, 0.0, format="%.6f")
    color = lc_expander.text_input('Cor', "red")

    lc_expander.write("Registre o local do ponto de referência no servidor, somente o administrador poderá apagar e ficará disponível para outros usuários:")
    if lc_expander.button("Registrar definitivamente"):
        lc_add = {'name': [lc_name], 'lat': [latitude], 'lon': [longitude], 'height': [height], 'color': [color]}
        if lc_name not in st.session_state.lc_df['name'].to_list():
            if re.match('^[A-Za-z0-9_-]*$', lc_add['name'][0]):
                st.session_state.lc_df = pd.concat([st.session_state.lc_df, pd.DataFrame(lc_add)], axis=0)
                st.session_state.lc_df.to_csv('data/confLocalWGS84.csv', index=False)
                lc_expander.write('Localização registrada')
            else:
                lc_expander.write('Escreva um nome sem caracteres especiais')
        else:
            lc_expander.write('Localização já existe')

    lc_expander.write("Registre o local do ponto de referência apenas para a sessão atual - não será gravado:")
    if lc_expander.button("Apenas para esta conversão"):
        lc_add = {'name': [lc_name], 'lat': [latitude], 'lon': [longitude], 'height': [height], 'color': [color]}
        if lc_name not in st.session_state.lc_df['name'].to_list():
            if re.match('^[A-Za-z0-9_-]*$', lc_add['name'][0]):
                st.session_state.lc_df = pd.concat([st.session_state.lc_df, pd.DataFrame(lc_add)], axis=0)
            else:
                lc_expander.write('Escreva um nome sem caracteres especiais')
        else:
            lc_expander.write('Localização já existe')
    # Carregar arquivo CSV
    lc_expander.write("Alternativamente pode ser carregado um arquivo csv com pontos de referência apenas para sessão atual ( name, color, lat, lon height)")
    uploaded_file = lc_expander.file_uploader("Pontos em um CSV para esta conversão", type="csv")
    if uploaded_file is not None:
        if uploaded_file.type == "text/csv":
            df = read_csv_index(uploaded_file)
            # Verifica se as colunas existem
            required_columns = {'name', 'lat', 'lon', 'height'}
            if required_columns.issubset(df.columns):
                # Verifica os tipos de dados das colunas
                if (df['name'].dtype == 'object' and df['lat'].dtype == 'float64' 
                    and df['lon'].dtype == 'float64' and df['height'].dtype == 'float64'):
                    st.session_state.lc_df = df
                    lc_expander.success("carregado com sucesso", icon= cn.SUCCESS)
                else:
                    lc_expander.error("error: o tipo de dado errado - esperado: name e color string e lat, lon e height float ", icon= cn.ERROR)
                    st.stop()
            else:
                lc_expander.error("error: colunas esperadas não estão presentes (name, color, lat, lon e height)", icon= cn.ERROR)
                st.stop()
        else:
            lc_expander.error("error: o arquivo não é csv", icon= cn.ERROR)
            st.stop()


def verifica_resultado(df):
    if df.shape[0]<1:
        st.error("sem dados", icon=cn.ERROR)
        st.stop()
    # Lista de colunas esperadas
    colunas_esperadas = ['lat', 'lon']    
    # Verificar se todas as colunas esperadas estão no DataFrame
    colunas_presentes = all(col in df.columns for col in colunas_esperadas)   
    if not colunas_presentes:
        st.info("sem informação de lat e lon, converta do dado", icon=cn.INFO)
        st.stop() 

    tipos_corretos = (
        (df['lat'].dtype == 'float64') and
        (df['lon'].dtype == 'float64')
    )
    
    if not tipos_corretos:
        st.info("tipo de dado incorreto de lat e lon ", icon=cn.INFO)
        st.stop()