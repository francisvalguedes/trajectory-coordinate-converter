"""
Creator: Francisval Guedes Soares
Date: 2024
"""

import streamlit as st
import pandas as pd
import re
import numpy as np
import pymap3d as pm

from lib.constants import  ConstantsNamespace
from lib.pgFunctions import*

import plotly.graph_objects as go
from plotly.subplots import make_subplots



# constants.py
cn = ConstantsNamespace()


def ler_verifica_csv(caminho_arquivo):
    try:
        # Lê o CSV ignorando a primeira linha (cabeçalho)
        df = pd.read_csv(caminho_arquivo,skiprows=[0], header=None)

        # Verifica se o CSV tem exatamente 3 colunas
        if df.shape[1] == 3:
            df.columns = ["x", "y", "z"]  # Renomeia as colunas para x, y, z
            st.success(f"Arquivo {caminho_arquivo.name} aceito", icon=cn.SUCCESS)
            return df
        else:
            st.error(f"Esperado 3 colunas, mas encontrou {df.shape[1]} em {caminho_arquivo.name}.", icon=cn.ERROR)
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}", icon=cn.ERROR)
        return pd.DataFrame()


def enu1_to_enu2(enu_rampa, ref_rampa, ref_sensor):
    ell=pm.Ellipsoid.from_name('wgs84')
    ecef = np.transpose(pm.enu2ecef(enu_rampa[:,0],
                                    enu_rampa[:,1],
                                    enu_rampa[:,2],
                                    ref_rampa["lat"],
                                    ref_rampa["lon"],
                                    ref_rampa["height"],
                                    ell=ell
                                    ))
    enu_sensor = np.transpose( pm.ecef2enu(
                                ecef[:,0],
                                ecef[:,1],
                                ecef[:,2],
                                ref_sensor["lat"],
                                ref_sensor["lon"],
                                ref_sensor["height"],
                                ell=ell
                                ))
    enu_azelr_radar = np.transpose(pm.enu2aer(enu_sensor[:,0],
                                        enu_sensor[:,1],
                                        enu_sensor[:,2],
                                        deg=False
                                        ))    
    enu_sensor = np.hstack((enu_sensor, enu_azelr_radar))
    return pd.DataFrame(enu_sensor, columns=['x', 'y', 'z', 'Az', 'El', 'd'])


def calculate_velocity_acceleration(df, sampling_time ):
    """
    Calcula a velocidade e aceleração para cada eixo e para as variáveis angulares (Az, El, r),
    e adiciona o tempo relativo ao primeiro ponto.

    Args:
        df (pd.DataFrame): DataFrame contendo as colunas 'x', 'y', 'z', 'Az', 'El', 'd'.
        sampling_time (float): Intervalo de tempo entre amostras (em segundos).

    Returns:
        pd.DataFrame: DataFrame com as colunas:
                      ['X(m)', 'Y(m)', 'Z(m)', 'VX(m/s)', 'VY(m/s)', 'VZ(m/s)', 
                       'AX(m/s²)', 'AY(m/s²)', 'AZ(m/s²)', 'Az', 'El', 'd', 
                       'Vaz(rad/s)', 'Vel(rad/s)', 'Vr(m/s)', 
                       'Aaz(rad/s²)', 'Ael(rad/s²)', 'Ar(m/s²)', 'Tempo (s)'].
    """
    # Calcular as diferenças das posições divididas pelo tempo de amostragem (velocidade)
    velocity_x = np.gradient(df['x'], sampling_time)
    velocity_y = np.gradient(df['y'], sampling_time)
    velocity_z = np.gradient(df['z'], sampling_time)

    # Ajustar descontinuidade angular para Az usando np.unwrap
    az_unwrapped = np.unwrap(df['Az'])  # Remove descontinuidade de 2pi em Az
    
    # Calcular as diferenças das variáveis angulares (Az, El, r) divididas pelo tempo (velocidade angular)
    velocity_az = np.gradient(az_unwrapped, sampling_time)  # Velocidade angular Azimute
    velocity_el = np.gradient(df['El'], sampling_time)  # Velocidade angular Elevação
    velocity_r = np.gradient(df['d'], sampling_time)    # Velocidade radial
   
    # Calcular as diferenças das velocidades divididas pelo tempo de amostragem (aceleração)
    acceleration_x = np.gradient(velocity_x, sampling_time)
    acceleration_y = np.gradient(velocity_y, sampling_time)
    acceleration_z = np.gradient(velocity_z, sampling_time)
    
    # Calcular as acelerações angulares (derivadas das velocidades angulares)
    acceleration_az = np.gradient(velocity_az, sampling_time)  # Aceleração angular Azimute
    acceleration_el = np.gradient(velocity_el, sampling_time)  # Aceleração angular Elevação
    acceleration_r = np.gradient(velocity_r, sampling_time)    # Aceleração radial


    # Criar um vetor de tempo relativo ao primeiro ponto
    time_relative = np.arange(0, len(df) * sampling_time, sampling_time)
    
    # Garantir que o vetor de tempo tenha o mesmo comprimento do DataFrame
    time_relative = time_relative[:len(df)]
    
    # Criar um novo DataFrame com os resultados
    result_df = pd.DataFrame({
        'TR(s)': time_relative,
        'X(m)': df['x'],
        'Y(m)': df['y'],
        'Z(m)': df['z'],
        'VX(m/s)': velocity_x,
        'VY(m/s)': velocity_y,
        'VZ(m/s)': velocity_z,
        'AX(m/s²)': acceleration_x,
        'AY(m/s²)': acceleration_y,
        'AZ(m/s²)': acceleration_z,
        'Az(rad)': az_unwrapped, #df['Az'],
        'El(rad)': df['El'],
        'd(m)': df['d'],
        'Vaz(rad/s)': velocity_az,
        'Vel(rad/s)': velocity_el,
        'Vr(m/s)': velocity_r,
        'Aaz(rad/s²)': acceleration_az,
        'Ael(rad/s²)': acceleration_el,
        'Ar(m/s²)': acceleration_r
   
    })   

    return result_df

def plot_streamlit_plotly(df, plot_seq, titulo = 'Gráficos Interativos'):
    """
    Gera 9 gráficos interativos (usando Plotly) para cada coluna do DataFrame fornecido, exceto a coluna de tempo ('Tempo (s)'),
    e exibe os gráficos na interface do Streamlit com interatividade (zoom, pan, hover).

    Args:
        df (pd.DataFrame): DataFrame com as colunas a serem plotadas. Deve conter uma coluna 'Tempo (s)'.
    """
    # # Determinar a sequência de colunas a serem plotadas (excluindo 'Tempo (s)')
    # plot_seq = df.columns.difference(['TR(s)'])
    
    # Criar uma figura com 9 subplots (usando o Layout do Plotly)
    fig = make_subplots(rows=3, cols=3, subplot_titles=plot_seq)
    
    # Adicionar gráficos para cada coluna do DataFrame
    for i, col_name in enumerate(plot_seq):
        row = i // 3 + 1  # Linha (1 a 3)
        col = i % 3 + 1   # Coluna (1 a 3)
        
        # Adicionar linha de dados para o gráfico interativo
        fig.add_trace(
            go.Scatter(x=df['TR(s)'], y=df[col_name], mode='lines', name=col_name),
            row=row, col=col
        )
    
    # Atualizar layout para melhorar a visualização
    fig.update_layout(
        height=900, width=1200,  # Tamanho total da figura
        title_text=titulo,
        showlegend=False,
        title_x=0.5,
        template="plotly" # "plotly_dark"  # Tema de fundo escuro (opcional)
    )
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)


def main(): 
# cabeçalho
    st.title("Cálculo de Velocidade, Aceleração")
    st.markdown("Suposição: dados dois referenciais ENU (East-North-Up), um posicionado em uma rampa, de onde decola um veículo e outro"
                " referencial em um sensor que mede a evolução da posição desse veículo. Nessas condições essa página cálcula a velocidade,"
                " aceleração e no referencial do sensor a partir de trajetórias nominais cartesianas sem ruído no referencial da rampa."
                " Ao carregar o arquivo com a trajetória e configurar parâmetros do usuário o sistema efetua a conversão para o referencial do sensor,"
                " calcula a primeira e segunda derivadas e apresenta resultados de forma interativa com gráficos e tabelas")
    st.subheader('**Entrada de Configurações**')
    

    if "lc_df" not in st.session_state:
        st.session_state.lc_df = pd_csv_read('data/confLocalWGS84.csv')

    #Cadastra sensor sidebar
    sensor_registration()

# verifica se foi escolhido o sensor
    st.session_state.rampa = st.selectbox("Escolha o ponto de referência de origem - Rampa (ENU¹)",st.session_state.lc_df['name'].tolist())
    st.session_state.sensor = st.selectbox("Escolha o ponto de referência de destino - sensor (ENU²)",st.session_state.lc_df['name'].tolist())    
   
    # Entrada numérica para erro de distância em metros
    tempo_amostra = st.number_input('Tempo de amostragem (s)', min_value=0.01, max_value=10.0, value=1.0, step=0.01)
 
# carregar arquivo de pontos a serem convertidos
    st.markdown("""
    #### Arquivo a ser carregado:
    1. O arquivo de texto deve conter apenas 3 colunas 'x', 'y', 'z' no referencial plano local ENU (x-east, y-north, z-up) da rampa em m.
    2. O tempo de amostragem dos dados deve ser escolhido acima.
    3. Se o dado de entrada tiver passado por interpolação linear o cálculo da aceleração ficaráo errado.
    4. Exemplo de formato do arquivo (você pode baixa-lo clicando no icone no canto direito superior da tabela):
                """)

    ex6 = read_csv_index('data/p6_exemplo.csv')
    exp_ex6 = st.expander("Exemplo de arquivo a ser carregado", expanded=True)
    exp_ex6.dataframe( ex6.style.format(thousands=""))


    # Inicializa o estado da sessão para armazenar arquivos únicos por nome
    if "file_dict" not in st.session_state:
        st.session_state.file_dict = {}  # Dicionário {nome: dataframe}

    # Upload de múltiplos arquivos
    uploaded_files = st.file_uploader("Escolha um ou mais arquivos:", 
        accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name  # Obtém o nome do arquivo

            # Verifica se o nome do arquivo já foi carregado
            if file_name not in st.session_state.file_dict:
                #df = pd.read_csv(uploaded_file)
                df = ler_verifica_csv(uploaded_file)
                if len(df.index)>0:
                    st.session_state.file_dict[file_name] = df


    # Lista de arquivos carregados para exibir no selectbox
    file_names = list(st.session_state.file_dict.keys())

    if file_names:
        selected_file = st.selectbox("Selecione um arquivo:", file_names)

        # Exibir conteúdo do arquivo selecionado
        if selected_file:
            # st.write(f"Exibindo: **{selected_file}**")

            exp_loaded = st.expander("Arquivo carregado:", expanded=True)
            exp_loaded.dataframe(st.session_state.file_dict[selected_file])

            df_enu_rampa = st.session_state.file_dict[selected_file]
                
            if len(df_enu_rampa.index)>2000 or tempo_amostra < 1:
                st.warning('Se a amostragem tiver sido aumentada com interpolação linear o calculo fica comprometido', icon=cn.WARNING)
            st.write(f"Analisando o arquivo: {selected_file}, no referencial da rampa")
            # st.write(df_enu_rampa)
            reframpa = st.session_state.lc_df[st.session_state.lc_df['name'] == st.session_state.rampa].to_dict('records')[0]
            refsensor = st.session_state.lc_df[st.session_state.lc_df['name'] == st.session_state.sensor].to_dict('records')[0]
            if st.session_state.rampa == st.session_state.sensor:
                st.warning("sensor e rampa são o mesmo sistema de referência", icon=cn.WARNING)
                df_enu_sensor = enu1_to_enu2(df_enu_rampa.to_numpy(), reframpa, refsensor)
            else:
                df_enu_sensor = enu1_to_enu2(df_enu_rampa.to_numpy(), reframpa, refsensor)
            # st.write(df_enu_sensor)
            st.subheader('**Resultados:**')
            
            result_df = calculate_velocity_acceleration(df_enu_sensor, tempo_amostra)
            st.dataframe(result_df)

            result_df = result_df.iloc[3:-3] # ignora descontinuidade inicial e final

            st.subheader('**Gráficos:**')
            plot_seq = [ 'X(m)', 'Y(m)', 'Z(m)', 'VX(m/s)', 'VY(m/s)', 'VZ(m/s)', 'AX(m/s²)', 'AY(m/s²)', 'AZ(m/s²)']
            plot_streamlit_plotly(result_df, plot_seq, titulo='Gráfico de coordenadas cartesianas ENU sensor')
            plot_seq = ['Az(rad)', 'El(rad)', 'd(m)','Vaz(rad/s)', 'Vel(rad/s)', 'Vr(m/s)', 'Aaz(rad/s²)', 'Ael(rad/s²)', 'Ar(m/s²)']
            plot_streamlit_plotly(result_df, plot_seq, titulo='Gráfico de coordenadas polares do sensor')



if __name__== '__main__':
    main()