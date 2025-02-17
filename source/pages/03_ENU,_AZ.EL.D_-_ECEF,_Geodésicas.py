"""
Creator: Francisval Guedes Soares
Date: 2024
"""

import streamlit as st
import pandas as pd
from lib.constants import  ConstantsNamespace
from lib.pgFunctions import*
from lib.mapFunctions import*
import re
import numpy as np
import pymap3d as pm

cn = ConstantsNamespace()

def fit_data(df, lc):    
    ell=pm.Ellipsoid.from_name('wgs84')
    colunas_esperadas = ['x', 'y', 'z'] 
    # Verificar se todas as colunas esperadas estão no DataFrame
    colunas_presentes = all(col in df.columns for col in colunas_esperadas)  
    if not colunas_presentes:
        colunas_esperadas = ['Az', 'El', 'r']    
        # Verificar se todas as colunas esperadas estão no DataFrame
        colunas_presentes = all(col in df.columns for col in colunas_esperadas)   
        if not colunas_presentes:
            st.error("error: verifique se as colunas obrigatórias estão presente", icon=cn.ERROR)
            st.stop()
        else:
            ecef = np.transpose(pm.aer2ecef(df['Az'].to_numpy(), df['El'].to_numpy(), df['r'].to_numpy(), lc["lat"],lc["lon"], lc["height"], ell=ell))
            # pm.aer2ecef(az, el, srange, lat0, lon0, alt0, ell=None, deg=True)
            enu = np.transpose(pm.aer2enu(df['Az'].to_numpy(), df['El'].to_numpy(), df['r'].to_numpy()))
            df2 = pd.DataFrame(np.concatenate((enu, ecef), axis=1), columns=['x_'+lc['name'], 'y_'+lc['name'],'z_'+lc['name'],'ECEF_X', 'ECEF_Y','ECEF_Z'])
    else:
        azelr = np.transpose(pm.enu2aer(df['x'].to_numpy(), df['y'].to_numpy(), df['z'].to_numpy(), deg=True))
        # pm.enu2geodetic(e, n, u, lat0, lon0, h0, ell=None, deg=True)
        ecef = np.transpose(pm.enu2ecef(df['x'].to_numpy(), df['y'].to_numpy(), df['z'].to_numpy(), lc["lat"],lc["lon"], lc["height"], ell=ell))
        df2 = pd.DataFrame(np.concatenate((azelr, ecef), axis=1), columns=['az_'+lc['name'], 'el_'+lc['name'],'r_'+lc['name'],'ECEF_X', 'ECEF_Y','ECEF_Z'])
    
    df = data_concat(df ,df2)
    geodetic = np.transpose(pm.ecef2geodetic(ecef[:,0], ecef[:,1], ecef[:,2]))
    df2 = pd.DataFrame(geodetic, columns=['lat', 'lon','height'])
    df = data_concat(df ,df2)  
    return df

def main(): 
# configuração da página   
    st.set_page_config(
    page_title="ENU xyz para",
    page_icon="🌏", # "🤖",  # "🧊",
    # https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     'Get Help': 'https://www.sitelink.com',
    #     'Report a bug': "https://www.sitelink.com",
    #     'About': "# A cool app"
    # }
    )

# cabeçalho
    st.title("Conversão de coordenadas")
    st.subheader('**Conversão a partir de coordenadas ENU xyz**')
    
    st.markdown('Conversão de coordenadas ENU xyz para coordenadas ECEF, Geodésicas e azimute elevação e distância em um ponto de referência')
    st.markdown('Novos pontos de referências podem ser cadastrados na barra lateral')

    if "lc_df" not in st.session_state:
        st.session_state.lc_df = pd_csv_read('data/confLocalWGS84.csv')

    c_ref = st.session_state.lc_df

    #Cadastra sensor sidebar
    sensor_registration()

# verifica se foi escolhido o sensor
    #st.session_state.sensores = st.multiselect('Escolha os sensores para conversão', c_ref['name'].tolist())
    st.session_state.sensores = st.selectbox("Escolha um ponto de referência para conversão",c_ref['name'].tolist(),)    
    if len(st.session_state.sensores)<1:
        st.info('Selecione um ponto de referência', icon=cn.INFO)
        st.stop()

    # Escolher método de entrada
    input_method = st.radio("Escolha o método de entrada de dados:", ("Manual(ENU)", "Manual(Az, El, Range)", "Arquivo CSV"))
    if input_method == "Manual(ENU)":
        # Entrada de dados manual
        st.write("Insira os dados do ponto:")
        df_pontos = data_input_enu()
    elif input_method == "Manual(Az, El, Range)":
        # Entrada de dados manual
        st.write("Insira os dados do ponto:")        
        df_pontos = data_input_azelr()

    elif input_method == "Arquivo CSV":
# carregar arquivo de pontos a serem convertidos
        st.markdown("""
        #### Arquivo a ser carregado:
        1. O arquivo CSV deve conter as colunas 'x', 'y', 'z' ou 'Az', 'El', 'r', se contiver ambas será convertido 'x', 'y', 'z'.
        2. As coordenadas 'x', 'y', 'z' ou 'Az', 'El', 'r' devem estar no formato decimal - float.
        3. A coluna 'color' (ex: pink) é opcionais para plotagem no mapa.
        4. Exemplo de formato do arquivo CSV (você pode baixa-lo clicando no icone no canto direito superior da tabela):
        """)
        ex3 = read_csv_index('data/p3_exemplo.csv')
        st.dataframe( ex3.dropna(how='all').style.format(thousands=""))

        mkm = st.selectbox("Unidade métrica do dado de entrada", ['m', 'km'])
        radgraus = st.selectbox("Unidade angular do dado de entrada", ['graus', 'rad'])

        data_elements = st.file_uploader("Carregue as coordenadas que deseja converter (nome, x, y, z) ou (nome, Az, El, r) - csv",type='csv')
        if data_elements is not None:
            st.write("File details:")
            file_details = {"Filename":data_elements.name,"FileType":data_elements.type,"FileSize":data_elements.size}
            st.write(file_details)
            #st.write("Orbital elements manually updated:")    
            if data_elements.type == "text/csv":
                df_pontos = read_csv_index(data_elements)
                df_pontos = converter_unidades(df_pontos, mkm, radgraus)
                st.dataframe(df_pontos) 
            else:
                st.error("error: verifique o formato do arquivo", icon= cn.ERROR)
                st.stop()
        
# verifica 
    if 'df_pontos' not in locals():
        st.info("Sem dado, carregue o arquivo", icon=cn.INFO)
        st.stop()

    st.markdown('Converter pontos carregados:')
    if st.button("Converter"): 
        lc = c_ref.loc[c_ref['name'] == st.session_state.sensores].to_dict('records')[0]            
        st.session_state.df_pontos = fit_data(df_pontos.copy(deep=True), lc)

    if 'df_pontos' not in st.session_state:
        st.info("Dado ainda não convertido, converta do dado", icon=cn.INFO)
        st.stop()

    st.markdown('Resultado da conversão:')
    verifica_resultado(st.session_state.df_pontos)       

    st.dataframe(st.session_state.df_pontos)

    existing_columns = st.session_state.df_pontos.columns.intersection(['name', 'lat', 'lon', 'height', 'color', 'size'])
    df_map = data_map_concat(st.session_state.df_pontos[existing_columns].copy(deep=True),
                             c_ref.loc[c_ref['name']==st.session_state.sensores].copy(deep=True))
    #st.dataframe(df_map)
    # st.map(df_map, latitude="lat", longitude="lon", size="size", color="color_ex")
    gdf_data = upload_geojson()
    # Criar o mapa
    st.write('Pontos no mapa:')
    mapa = create_map2(df_map, gdf_data)
    # Exibir o mapa no Streamlit
    st.components.v1.html(folium.Figure().add_child(mapa).render(), height=600)
    # page_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH',  want_output = True,)        
    #st_folium(mapa, width=page_width)  #height=600,  

if __name__== '__main__':
    main()
