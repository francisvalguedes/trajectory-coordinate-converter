import streamlit as st
import pandas as pd
import numpy as np
import pymap3d as pm
import re

from lib.constants import  ConstantsNamespace
from lib.pgFunctions import*
from lib.mapFunctions import*

cn = ConstantsNamespace()

def main():
    st.set_page_config(page_title="Geodésicas para", page_icon="🌏", layout="wide")
    st.title("Conversão de Coordenadas")
    st.subheader('**Conversão a partir de coordenadas Geodésicas WGS84**')
    st.markdown('Conversão de coordenadas Geodésicas (latitude, longitude e altitude) para coordenadas ECEF, ENU e azimute, elevação e distância em um ponto de referência')

# ler arquivo de pontos de referências (sensor)
    st.markdown('Novos pontos de referências podem ser cadastrados na barra lateral')

    if "lc_df" not in st.session_state:
        st.session_state.lc_df = pd_csv_read('data/confLocalWGS84.csv')

# adicionar novo ponto de referência (sensor)
    sensor_registration()

# Seleciona os pontos de referência (sensores) para conversão 
    st.session_state.sensores = st.multiselect('Escolha os pontos de referência (sensores) para conversão',
                                                st.session_state.lc_df['name'].tolist(),
                                                default=st.session_state.lc_df['name'].tolist())
    if len(st.session_state.sensores) < 1:
        st.info('Selecione os pontos de referência (sensores)', icon=cn.INFO)

    # Escolher método de entrada
    input_method = st.radio("Escolha o método de entrada de dados:", ("Manual", "Arquivo CSV"))
    if input_method == "Manual":
        # Entrada de dados manual
        st.write("Insira os dados do ponto:")
        df_pontos = data_input_geodesicas()

    else:
    # carrega o arquivo para conversão
        st.markdown("""
        #### Arquivo a ser carregado:
        1. O arquivo CSV deve conter as obrigatoriamente as colunas 'lat', 'lon' e height.
        2. As coordenadas 'lat' e 'lon' devem estar no formato decimal (float ou int).
        3. A coordenada height devem se decimal ou inteiro (float ou int).
        4. As colunas 'name' e 'color' (ex: pink) são opcionais para plotagem no mapa.        
        5. Exemplo de formato do arquivo CSV (você pode baixa-lo clicando no icone no canto direito superior da tabela):
        """)
        ex1 = read_csv_index('data/p11_exemplo.csv')

        st.dataframe( ex1.style.format(thousands=""))

        data_elements = st.file_uploader("Carregue o arquivo que deseja converter - csv", type='csv')
        if data_elements is not None:        
            df_pontos = read_csv_index(data_elements)
            st.markdown('Pontos carregados:') 
            st.dataframe(df_pontos)
            df_pontos = find_coord_geod(df_pontos)            
        
    if 'df_pontos' not in locals():
        st.info("Sem dado, carregue o arquivo", icon=cn.INFO)
        st.stop()
    else:
# coloca os dados no mapa
        st.write('Pontos no mapa:')
        dados_sensores = st.session_state.lc_df['name'].isin(st.session_state.sensores)
        df_map = data_map_concat(df_pontos.copy(), st.session_state.lc_df.loc[dados_sensores].copy())
        # st.map(df_map, latitude="lat", longitude="lon", size="size", color="color_ex")
        gdf_data = upload_geojson()
        # Criar o mapa
        mapa = create_map2(df_map, gdf_data)
        # Exibir o mapa no Streamlit
        st.components.v1.html(folium.Figure().add_child(mapa).render(), height=600)
        # page_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH',  want_output = True,)        
        #st_folium(mapa, width=page_width)  #height=600,  

    if st.button("Converter"):
        for sensor_sel in st.session_state.sensores:
            lc = st.session_state.lc_df.loc[st.session_state.lc_df['name'] == sensor_sel].to_dict('records')[0]
            AzElr = np.transpose(pm.geodetic2aer(df_pontos["lat"], df_pontos["lon"], df_pontos["height"], lc["lat"], lc["lon"], lc["height"]))
            enu = np.transpose(pm.geodetic2enu(df_pontos["lat"], df_pontos["lon"], df_pontos["height"], lc["lat"], lc["lon"], lc["height"]))
            df_pontos = data_concat(df_pontos, pd.DataFrame(AzElr, columns=['Az_' + sensor_sel, 'El_' + sensor_sel, 'r_' + sensor_sel]))
            df_pontos = data_concat(df_pontos, pd.DataFrame(enu, columns=['x_' + sensor_sel, 'y_' + sensor_sel, 'z_' + sensor_sel]))
        ecef = np.transpose(pm.geodetic2ecef(df_pontos["lat"], df_pontos["lon"], df_pontos["height"]))
        df_pontos = data_concat(df_pontos, pd.DataFrame(ecef, columns=['ECEF_X', 'ECEF_Y', 'ECEF_Z']))
        st.markdown('Resultado da conversão (você pode baixar os dados clicando no icone no canto direito superior da tabela):')
        st.dataframe(df_pontos)
        if len(st.session_state.sensores)<1:
            st.info('Nenhum ponto de referência selecionado, feita apenas a conversões para ECEF', icon=cn.INFO)


if __name__ == '__main__':
    main()
