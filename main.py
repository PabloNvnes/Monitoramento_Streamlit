import streamlit as st
from datetime import datetime, timedelta
import pytz
from pysolar.solar import get_altitude
from pysolar.radiation import get_radiation_direct
import pandas as pd
import plotly.express as px

###############
##  Funções  ## 
###############

# Função para obter dados de irradiância solar
def get_solar_irradiance(lat, lon, date_time):
    altitude = get_altitude(lat, lon, date_time)
    if altitude > 0:
        irradiance = get_radiation_direct(date_time, altitude)
    else:
        irradiance = 0
    return irradiance

# Função para calcular a performance do inversor solar
def calculate_inverter_performance(irradiance, efficiency=0.20):
    return irradiance * efficiency

def irradiancia():

    # Lista de cidades representativas de cada estado do Brasil com suas coordenadas
    cities = [
        {"state": "São Paulo", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo"},
        {"state": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729, "timezone": "America/Sao_Paulo"},
        {"state": "Minas Gerais", "lat": -19.9167, "lon": -43.9345, "timezone": "America/Sao_Paulo"},
        {"state": "Distrito Federal", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo"},
        {"state": "Bahia", "lat": -12.9714, "lon": -38.5014, "timezone": "America/Bahia"},
        {"state": "Ceará", "lat": -3.7172, "lon": -38.5434, "timezone": "America/Fortaleza"},
        {"state": "Paraná", "lat": -25.4284, "lon": -49.2733, "timezone": "America/Sao_Paulo"},
        {"state": "Amazonas", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus"},
        {"state": "Pernambuco", "lat": -8.0476, "lon": -34.8770, "timezone": "America/Recife"},
        {"state": "Rio Grande do Sul", "lat": -30.0346, "lon": -51.2177, "timezone": "America/Sao_Paulo"},
        {"state": "Pará", "lat": -1.4558, "lon": -48.4902, "timezone": "America/Belem"},
        {"state": "Goiás", "lat": -16.6869, "lon": -49.2648, "timezone": "America/Sao_Paulo"},
        {"state": "Maranhão", "lat": -2.5307, "lon": -44.3068, "timezone": "America/Fortaleza"},
        {"state": "Alagoas", "lat": -9.6658, "lon": -35.7350, "timezone": "America/Maceio"},
        {"state": "Rio Grande do Norte", "lat": -5.7945, "lon": -35.2110, "timezone": "America/Fortaleza"},
        {"state": "Piauí", "lat": -5.0919, "lon": -42.8034, "timezone": "America/Fortaleza"},
        {"state": "Paraíba", "lat": -7.1195, "lon": -34.8450, "timezone": "America/Fortaleza"},
        {"state": "Sergipe", "lat": -10.9472, "lon": -37.0731, "timezone": "America/Maceio"},
        {"state": "Mato Grosso do Sul", "lat": -20.4697, "lon": -54.6201, "timezone": "America/Campo_Grande"},
        {"state": "Mato Grosso", "lat": -15.6014, "lon": -56.0979, "timezone": "America/Cuiaba"},
        {"state": "Tocantins", "lat": -10.2491, "lon": -48.3243, "timezone": "America/Araguaina"},
        {"state": "Roraima", "lat": 2.8235, "lon": -60.6758, "timezone": "America/Boa_Vista"},
        {"state": "Amapá", "lat": 0.0340, "lon": -51.0694, "timezone": "America/Belem"},
        {"state": "Rondônia", "lat": -8.7612, "lon": -63.9039, "timezone": "America/Porto_Velho"},
        {"state": "Acre", "lat": -9.9747, "lon": -67.8243, "timezone": "America/Rio_Branco"}
    ]

    # Obter dados de irradiância solar para as últimas 24 horas para cada cidade
    irradiance_data = {city["state"]: [] for city in cities}
    time_data = []
    current_time = datetime.now(pytz.utc)
    for hour in range(24):
        time_point = current_time - timedelta(hours=hour)
        time_data.append(time_point)
        for city in cities:
            timezone = pytz.timezone(city["timezone"])
            local_time = time_point.astimezone(timezone)
            irradiance = get_solar_irradiance(city["lat"], city["lon"], local_time)
            irradiance_data[city["state"]].append(irradiance)

    # Calcular a irradiância solar total para cada estado
    total_irradiance = {state: sum(irradiance_data[state]) for state in irradiance_data}

    # Criar DataFrame para facilitar a manipulação dos dados
    df = pd.DataFrame(irradiance_data, index=time_data)

    # Inverter os dados para que o tempo esteja em ordem crescente
    df = df.iloc[::-1]

    # Criar DataFrame para a soma total da irradiância
    df_total_irradiance = pd.DataFrame(list(total_irradiance.items()), columns=['Estado', 'Irradiância Total (W/m²)'])

    # Criar gráfico de barras com Plotly Express
    fig_bar = px.bar(df_total_irradiance, x='Estado', y='Irradiância Total (W/m²)', title='Irradiância Solar Total por Estado nas Últimas 24 Horas')
    fig_bar.update_layout(xaxis_title='Estado', yaxis_title='Irradiância Total (W/m²)', legend_title_text='Estado')

    # Exibir o gráfico de barras no Streamlit
    st.title('Irradiância Solar Total por Estado nas Últimas 24 Horas')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Criar gráfico de linhas com Plotly Express
    fig_line = px.line(df, x=df.index, y=df.columns, labels={'value': 'Irradiância Solar (W/m²)', 'index': 'Hora'}, title='Irradiância Solar nas Últimas 24 Horas')
    fig_line.update_layout(xaxis_title='Hora', yaxis_title='Irradiância Solar (W/m²)', legend_title_text='Estado')

    # Exibir o gráfico de linhas no Streamlit
    st.plotly_chart(fig_line, use_container_width=True)

def performance():
    # Lista de cidades representativas de cada estado do Brasil com suas coordenadas
    cities = [
        {"state": "São Paulo", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo"},
        {"state": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729, "timezone": "America/Sao_Paulo"},
        {"state": "Minas Gerais", "lat": -19.9167, "lon": -43.9345, "timezone": "America/Sao_Paulo"},
        {"state": "Distrito Federal", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo"},
        {"state": "Bahia", "lat": -12.9714, "lon": -38.5014, "timezone": "America/Bahia"},
        {"state": "Ceará", "lat": -3.7172, "lon": -38.5434, "timezone": "America/Fortaleza"},
        {"state": "Paraná", "lat": -25.4284, "lon": -49.2733, "timezone": "America/Sao_Paulo"},
        {"state": "Amazonas", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus"},
        {"state": "Pernambuco", "lat": -8.0476, "lon": -34.8770, "timezone": "America/Recife"},
        {"state": "Rio Grande do Sul", "lat": -30.0346, "lon": -51.2177, "timezone": "America/Sao_Paulo"},
        {"state": "Pará", "lat": -1.4558, "lon": -48.4902, "timezone": "America/Belem"},
        {"state": "Goiás", "lat": -16.6869, "lon": -49.2648, "timezone": "America/Sao_Paulo"},
        {"state": "Maranhão", "lat": -2.5307, "lon": -44.3068, "timezone": "America/Fortaleza"},
        {"state": "Alagoas", "lat": -9.6658, "lon": -35.7350, "timezone": "America/Maceio"},
        {"state": "Rio Grande do Norte", "lat": -5.7945, "lon": -35.2110, "timezone": "America/Fortaleza"},
        {"state": "Piauí", "lat": -5.0919, "lon": -42.8034, "timezone": "America/Fortaleza"},
        {"state": "Paraíba", "lat": -7.1195, "lon": -34.8450, "timezone": "America/Fortaleza"},
        {"state": "Sergipe", "lat": -10.9472, "lon": -37.0731, "timezone": "America/Maceio"},
        {"state": "Mato Grosso do Sul", "lat": -20.4697, "lon": -54.6201, "timezone": "America/Campo_Grande"},
        {"state": "Mato Grosso", "lat": -15.6014, "lon": -56.0979, "timezone": "America/Cuiaba"},
        {"state": "Tocantins", "lat": -10.2491, "lon": -48.3243, "timezone": "America/Araguaina"},
        {"state": "Roraima", "lat": 2.8235, "lon": -60.6758, "timezone": "America/Boa_Vista"},
        {"state": "Amapá", "lat": 0.0340, "lon": -51.0694, "timezone": "America/Belem"},
        {"state": "Rondônia", "lat": -8.7612, "lon": -63.9039, "timezone": "America/Porto_Velho"},
        {"state": "Acre", "lat": -9.9747, "lon": -67.8243, "timezone": "America/Rio_Branco"}
    ]

    # Obter dados de irradiância solar para as últimas 24 horas para cada cidade a cada 5 minutos
    performance_data = {city["state"]: [] for city in cities}
    time_data = []
    current_time = datetime.now(pytz.utc)
    for minute in range(0, 24 * 60, 5):
        time_point = current_time - timedelta(minutes=minute)
        time_data.append(time_point)
        for city in cities:
            timezone = pytz.timezone(city["timezone"])
            local_time = time_point.astimezone(timezone)
            irradiance = get_solar_irradiance(city["lat"], city["lon"], local_time)
            performance = calculate_inverter_performance(irradiance)
            performance_data[city["state"]].append(performance)

    # Criar DataFrame para facilitar a manipulação dos dados
    df_performance = pd.DataFrame(performance_data, index=time_data)

    # Inverter os dados para que o tempo esteja em ordem crescente
    df_performance = df_performance.iloc[::-1]

    # Criar gráfico de linhas com Plotly Express
    fig_performance = px.line(df_performance, x=df_performance.index, y=df_performance.columns, labels={'value': 'Performance do Inversor (W)', 'index': 'Hora'}, title='Performance do Inversor Solar a Cada 5 Minutos')
    fig_performance.update_layout(xaxis_title='Hora', yaxis_title='Performance do Inversor (W)', legend_title_text='Estado')

    # Exibir o gráfico de linhas no Streamlit
    st.title('Performance do Inversor Solar a Cada 5 Minutos')
    st.plotly_chart(fig_performance, use_container_width=True)

def disponibilidade():
    return

#####################
## Streamlit Geral ##
#####################

# Adicionar uma barra lateral
add_sidebar = st.sidebar.selectbox('Análises', ('Irradiância Solar', 'Performance dos Estados', 'Disponibilidade de Energia'))

#################
## Irradiância ##
#################

if add_sidebar == 'Irradiância Solar':
    st.title('Irradiância Solar')

    irradiancia()

#############################
## Performance dos Estados ##
#############################

if add_sidebar == 'Performance e disponibilidade das Usinas':
    st.title('Performance e disponibilidade das Usinas')

    performance()

################################
## Disponibilidade de Energia ##
################################

if add_sidebar == 'Disponibilidade de Energia':
    st.title('Disponibilidade de Energia')

    disponibilidade()