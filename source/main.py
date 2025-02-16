"""
Creator: Francisval Guedes Soares
Date: 2021
"""

import streamlit as st
from datetime import datetime
from lib.pgFunctions import*

def main():
    """main function that provides the simplified interface for configuration,
         visualization and data download. """  

    st.set_page_config(
    page_title="Conversão de Coordenadas",
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

    st.title("Conversão de Coordenadas")
    st.subheader('**Conversão de coordenadas de trajetórias espaciais entre sistemas de referência terestres**')

    st.markdown('Iniciado por: Francisval Guedes Soares, Email: francisvalg@gmail.com')
    
    url = "https://github.com/francisvalguedes/trajectory-coordinate-converter.git"
    st.markdown("Repositório: [github.com/francisvalguedes/trajectory-coordinate-converter](%s)" % url)

    ## Descrição                
    st.markdown("""
    Aplicação web desenvolvida com Streamlit que permite a conversão de coordenadas entre alguns sistemas de referência, considera o elipsoide WGS84. Admite entrada manual de um ponto ou a partir de arquivo CSV contendo, por exemplo, uma trajetória com milhares de pontos. A aplicação utiliza as bibliotecas `pandas`, `numpy` e `pymap3d` para realizar as conversões necessárias e a biblioteca `Folium` e  `plotly` para mostrar os dados no mapa e em gráficos.

    Escolha a página desejada na barra lateral:
                
    ### Funcionalidades
    A aplicação possui quatro páginas principais:
                
    0. **Main**: Página de apresentação e cadastro de ponto de referência sensor, o cadastro pode ser somente para a sessão atual ou definitivo a escolha do usuário.
    1. **Conversão entre Grau DMS e Decimal**: Converte coordenadas de graus(degree), minutos e segundos (DMS) para graus decimais ou o contrário.
    2. **Conversão de Coordenadas Geodésicas para ECEF e ENU Plano Local**: Converte coordenadas geodésicas para ECEF (Earth-Centered, Earth-Fixed), para ENU (East-North-Up) plano local e azimute, elevação e distância.
    3. **Conversão de Coordenadas Plano Local ENU (XYZ) ou Azimute, Elevação e Distância em ECEF e Geodésicas**: Converte coordenadas de plano local ENU (XYZ) ou azimute, elevação e distância para ECEF e coordenadas geodésicas (latitude, longitude e altitude).
    4. **Conversão de Coordenadas Plano Local de referência ENU para outro plano local ENU**: Converte coordenadas de plano local ENU (XYZ) ou azimute, elevação e distância para outro plano local ENU (XYZ) e azimute, elevação e distância, e também para ECEF e coordenadas geodésicas .
    5. **Conversão de Coordenadas Geocentricas X,Y,Z para plano local ENU**: Converte coordenadas geocêntricas cartesianas (XYZ) para plano local ENU (XYZ) e azimute, elevação e distância, e também para geodésicas .
    6. **Velocidade e Aceleração de Trajetória ENU**:  Realiza cálculos de velocidade, aceleração e bandas passantes (para azimute elevação e distância) a partir de trajetórias nominais cartesianas sem ruído em referenciais locais ENU (East-North-Up). Ao carregar o arquivo CSV com a trajetória e configurar parâmetros do usuário obtêm-se os resultados de forma interativa com gráficos e tabelas .
    
    Abaixo a figura representa os sistemas de referência envolvidos no elipsoide WGS84.       
    """)

    st.image("figure/fig_ecef.png", caption="Sistemas de referência envolvidos")

    st.markdown('Novos pontos de referências podem ser cadastrados na barra lateral')
    st.markdown('Pontos de referência já cadastrados:')
    st.session_state.lc_df = pd.read_csv('data/confLocalWGS84.csv').dropna(how='all')
    st.dataframe(st.session_state.lc_df.style.format({'lat': '{:.6f}', 'lon': '{:.6f}', 'height': '{:.2f}'}))

    #Cadastra sensor sidebar
    sensor_registration()



        
if __name__== '__main__':
    main()