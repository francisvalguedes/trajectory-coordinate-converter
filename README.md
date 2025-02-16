# trajectory-coordinate-converter

## Descrição
O `trajectory-coordinate-converter` é uma aplicação web desenvolvida com Streamlit que permite a conversão de coordenadas a partir de arquivos CSV ou manualmente. A aplicação utiliza as bibliotecas `pandas`, `numpy`, `pymap3d` e `Folium` para realizar as conversões necessárias e mostrar dados em um mapa. O ellipsoid WGS84 é utilizado como padrão.

## Funcionalidades
A aplicação possui as páginas principais:
1. **Main**: Página de apresentação e cadastro de ponto de referência sensor.
2. **Conversão entre Grau DMS e Decimal**: Converte coordenadas de graus(degree), minutos e segundos (DMS) para graus decimais ou o contrário.
3. **Conversão de Coordenadas Geodésicas para ECEF e ENU Plano Local**: Converte coordenadas geodésicas para ECEF (Earth-Centered, Earth-Fixed), para ENU (East-North-Up) plano local e azimute, elevação e distância.
4. **Conversão de Coordenadas Plano Local ENU (XYZ) ou Azimute, Elevação e Distância em ECEF e Geodésicas**: Converte coordenadas de plano local ENU (XYZ) ou azimute, elevação e distância para ECEF e coordenadas geodésicas (latitude, longitude e altitude).
5. **Conversão de Coordenadas Plano Local de referência ENU para outro plano local ENU**: Converte coordenadas de plano local ENU (XYZ) ou azimute, elevação e distância para outro plano local ENU (XYZ) e azimute, elevação e distância, e também para ECEF e coordenadas geodésicas .
6. **Conversão de Coordenadas Geocentricas X,Y,Z para plano local ENU**: Converte coordenadas geocêntricas cartesianas (XYZ) para plano local ENU (XYZ) e azimute, elevação e distância, e também para geodésicas .
6. **Conversão de Coordenadas Geocentricas X,Y,Z para plano local ENU**:  Realiza cálculos de velocidade, aceleração e bandas passantes para azimute elevação e distância de trajetórias nominais cartesianas  sem ruído em referenciais locais ENU (East-North-Up). Ao carregar o arquivo CSV com a trajetória e configurar parâmetros do usuário obten-se os resultados de forma interativa com gráficos e tabelas .


## Instalação
Siga os passos abaixo para instalar e configurar o ambiente de desenvolvimento:

```bash
# Clone o repositório
git clone https://github.com/francisvalguedes/coordConverter.git

# Navegue até o diretório do projeto
cd coordConverter

# Crie um ambiente virtual
python -m venv env

# Ative o ambiente virtual
# No Windows
env\Scripts\activate
# No macOS/Linux
source env/bin/activate

# Instale as dependências
pip install -r requirements.txt

# execute
streamlit run source/main.py

```

## Uso
Para iniciar a aplicação, execute o seguinte comando:

```bash
streamlit run app.py
```

## Bibliotecas Utilizadas
1. pandas - BSD-3-Clause
2. numpy - BSD-3-Clause
3. streamlit - Apache 2.0
4. pymap3d - BSD-2-Clause

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.