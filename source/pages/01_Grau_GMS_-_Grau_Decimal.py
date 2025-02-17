import streamlit as st
import pandas as pd
import re

from lib.constants import  ConstantsNamespace
from lib.pgFunctions import  read_csv_index

cn = ConstantsNamespace()

# Função para converter DMS para DD
def dms_to_dd(dms_str):
    dms_str = dms_str.strip()
    sign = -1 if dms_str[0] == '-' else 1
    dms_str = dms_str[1:] if sign == -1 else dms_str
    d, m, s = re.split('[°\'"]', dms_str)[:3]
    return sign * (float(d) + float(m)/60 + float(s)/3600)

def dd_to_dms_string(decimal_degrees):
    is_positive = decimal_degrees >= 0
    decimal_degrees = abs(decimal_degrees)

    degrees = int(decimal_degrees)
    minutes = int((decimal_degrees - degrees) * 60)
    seconds = (decimal_degrees - degrees - minutes / 60) * 3600

    sign = '' if is_positive else '-'
    return f"{sign}{degrees}°{minutes}'{seconds:.6f}\""
    #return f"{sign}{degrees}°{minutes:02}'{seconds:02.6f}\""

def main():

    # Título e instruções
    st.title("Conversor Graus 'DMS' (GMS - grau(degree), minuto e segundo) para decimal ou de grau decimal para 'DMS' ")

    # Opção de entrada de dados
    st.subheader("Entrada de Dados")
    entrada_opcao = st.radio("Escolha o método de entrada:", ("Entrada Manual", "Upload de Arquivo CSV"))

    if entrada_opcao == "Entrada Manual":
        st.markdown("### Conversão Manual")
        
        # Entrada manual DMS para DD
        dms_lat = st.text_input("Latitude (em DMS, ex: 23°34'45.2459\")", value="23°34'45.2459\"")
        dms_lon = st.text_input("Longitude (em DMS, ex: 46°38'59.25\")", value="-0°14'54.2456\"")
        if st.button("Converter DMS para Decimal"):
            try:
                lat_dd = dms_to_dd(dms_lat)
                lon_dd = dms_to_dd(dms_lon)
                st.write(f"Latitude em Decimal: {lat_dd:.8f}")
                st.write(f"Longitude em Decimal: {lon_dd:.8f}")
            except Exception as e:
                st.error(f"Erro ao converter DMS para Decimal: {e}")

        # Entrada manual DD para DMS
        dd_lat = st.number_input("Latitude em Decimal", format="%.8f")
        dd_lon = st.number_input("Longitude em Decimal", format="%.8f")
        if st.button("Converter Decimal para DMS"):
            lat_dms = dd_to_dms_string(dd_lat)
            lon_dms = dd_to_dms_string(dd_lon)
            st.write(f"Latitude em DMS: {lat_dms}")
            st.write(f"Longitude em DMS: {lon_dms}")

    else:
        st.markdown("""
        ### Instruções:
        1. O arquivo CSV deve conter as colunas 'lat_dms' e 'lon_dms' ou 'lat' e 'lon'.
        2. As colunas 'lat_dms' e 'lon_dms' devem estar no formato de texto: graus, minutos e segundos DMS(GMS).
        3. As coordenadas 'lat' e 'lon' devem estar em graus decimal (float).
        4. Exemplos de formatos do arquivo CSV (pode ser baixado no topo direito de cada tabela):
        """)

        col1, col2 = st.columns(2)

        col1.markdown('Exemplo para converter de gms para decimal')
        col2.markdown('Exemplo para converter de decimal para gms')

        ex1 = read_csv_index('data/p12_exemplo.csv')
        ex2 = read_csv_index('data/p11_exemplo.csv')

        col1.dataframe( ex1.style.format(thousands=""))
        col2.dataframe( ex2.style.format(thousands=""))

        # Carregar arquivo CSV
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
        if uploaded_file is not None:
            if uploaded_file.type == "text/csv":
                df = read_csv_index(uploaded_file)
            else:
                st.error("error: o arquivo não é csv", icon= cn.ERROR)
                st.stop()
            

            # Verificar se as colunas 'lat' e 'lon' estão presentes
            if all(col in df.columns for col in ['lat', 'lon','lat_dms','lon_dms']):
                st.error("Este arquivo CSV já foi convertido e já possui as colunas 'lat_dms', 'lon_dms', 'lat' e 'lon'.", icon= cn.ERROR)
                st.stop()
            elif 'lat_dms' in df.columns and 'lon_dms' in df.columns:
                if all(df[col].dtype =='object' for col in  ['lat_dms','lon_dms']):
                    try:                    
                        # Converter DMS para DD
                        df['lat'] = df['lat_dms'].apply(dms_to_dd)
                        df['lon'] = df['lon_dms'].apply(dms_to_dd)
                        
                        st.write("Dados convertidos:")
                        st.dataframe(df)
                    except Exception as e:
                        st.error(f"Erro ao converter os dados verifique o formato de 'lat_dms' e 'lon_dms': {e}")              

                else:
                    st.error("Verifique se o tipo de dado está correto de 'lat_dms' e 'lon_dms'", icon=cn.ERROR)
                    st.stop()

            elif 'lat' in df.columns and 'lon' in df.columns:
                if not all(df[col].dtype in ['float64', 'int64'] for col in  ['lat','lon']):
                    st.error("Verifique se o tipo de dado está correto de 'lat' e 'lon'", icon=cn.ERROR)
                    st.stop()
                else:
                    df['lat_dms'] = df['lat'].apply(dd_to_dms_string)
                    df['lon_dms'] = df['lon'].apply(dd_to_dms_string)
                    
                    st.write("Dados convertidos:")
                    st.dataframe(df)

            else:
            #if ('lat_dms' in df.columns and 'lon_dms' in df.columns) or ('lat' in df.columns and 'lon' in df.columns):
                st.error("O arquivo CSV deve conter as colunas 'lat_dms' e 'lon_dms' ou 'lat' e 'lon'.", icon= cn.ERROR)
                st.stop()

        else:
            st.info("Por favor, faça o upload de um arquivo CSV.", icon= cn.INFO)


if __name__ == '__main__':
    main()