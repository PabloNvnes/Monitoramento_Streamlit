import streamlit as st
from datetime import datetime, timedelta
import pytz
from pysolar.solar import get_altitude
from pysolar.radiation import get_radiation_direct
import pandas as pd
import plotly.express as px
import random
import openpyxl
import os

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

def irradiancia(selected_usina=None):

    # Lista de usinas fictícias com suas coordenadas
    plants = [
        {"plant": "Usina 1", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo"},
        {"plant": "Usina 2", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo"},
        {"plant": "Usina 3", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus"}
    ]

    if selected_usina:
        plants = [plant for plant in plants if plant["plant"] == selected_usina]

    # Obter dados de irradiância solar para as últimas 24 horas para cada usina
    irradiance_data = {plant["plant"]: [] for plant in plants}
    time_data = []
    current_time = datetime.now(pytz.utc)
    for hour in range(24):
        time_point = current_time - timedelta(hours=hour)
        time_data.append(time_point)
        for plant in plants:
            timezone = pytz.timezone(plant["timezone"])
            local_time = time_point.astimezone(timezone)
            irradiance = get_solar_irradiance(plant["lat"], plant["lon"], local_time)
            irradiance_data[plant["plant"]].append(irradiance)

    # Calcular a irradiância solar total para cada usina
    total_irradiance = {plant: sum(irradiance_data[plant]) for plant in irradiance_data}

    # Criar DataFrame para facilitar a manipulação dos dados
    df = pd.DataFrame(irradiance_data, index=time_data)

    # Inverter os dados para que o tempo esteja em ordem crescente
    df = df.iloc[::-1]

    # Criar DataFrame para a soma total da irradiância
    df_total_irradiance = pd.DataFrame(list(total_irradiance.items()), columns=['Usina', 'Irradiância Total (W/m²)'])

    # Criar gráfico de barras com Plotly Express
    fig_bar = px.bar(df_total_irradiance, x='Usina', y='Irradiância Total (W/m²)', title='Irradiância Solar Total por Usina nas Últimas 24 Horas')
    fig_bar.update_layout(xaxis_title='Usina', yaxis_title='Irradiância Total (W/m²)', legend_title_text='Usina')

    # Exibir o gráfico de barras no Streamlit
    st.title('Irradiância Solar Total por Usina nas Últimas 24 Horas')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Criar gráfico de linhas com Plotly Express
    fig_line = px.line(df, x=df.index, y=df.columns, labels={'value': 'Irradiância Solar (W/m²)', 'index': 'Hora'}, title='Irradiância Solar nas Últimas 24 Horas')
    fig_line.update_layout(xaxis_title='Hora', yaxis_title='Irradiância Solar (W/m²)', legend_title_text='Usina')

    # Exibir o gráfico de linhas no Streamlit
    st.plotly_chart(fig_line, use_container_width=True)

def performance(selected_usina=None):
    # Lista de usinas fictícias com suas coordenadas
    plants = [
        {"plant": "Usina 1", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo"},
        {"plant": "Usina 2", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo"},
        {"plant": "Usina 3", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus"}
    ]

    if selected_usina:
        plants = [plant for plant in plants if plant["plant"] == selected_usina]

    # Obter dados de irradiância solar para as últimas 24 horas para cada usina a cada 5 minutos
    performance_data = {plant["plant"]: [] for plant in plants}
    time_data = []
    current_time = datetime.now(pytz.utc)
    for minute in range(0, 24 * 60, 5):
        time_point = current_time - timedelta(minutes=minute)
        time_data.append(time_point)
        for plant in plants:
            timezone = pytz.timezone(plant["timezone"])
            local_time = time_point.astimezone(timezone)
            irradiance = get_solar_irradiance(plant["lat"], plant["lon"], local_time)
            performance = calculate_inverter_performance(irradiance)
            # Simular problemas nos inversores
            if random.random() < 0.05:  # 5% de chance de problema
                performance *= random.uniform(0.5, 0.9)  # Reduzir performance entre 10% e 50%
            performance_data[plant["plant"]].append(performance)

    # Criar DataFrame para facilitar a manipulação dos dados
    df_performance = pd.DataFrame(performance_data, index=time_data)

    # Inverter os dados para que o tempo esteja em ordem crescente
    df_performance = df_performance.iloc[::-1]

    # Criar gráfico de linhas com Plotly Express
    fig_performance = px.line(df_performance, x=df_performance.index, y=df_performance.columns, labels={'value': 'Performance do Inversor (W)', 'index': 'Hora'}, title='Performance do Inversor Solar a Cada 5 Minutos')
    fig_performance.update_layout(xaxis_title='Hora', yaxis_title='Performance do Inversor (W)', legend_title_text='Usina')

    # Exibir o gráfico de linhas no Streamlit
    st.title('Performance do Inversor Solar a Cada 5 Minutos')
    st.plotly_chart(fig_performance, use_container_width=True)

    # Calcular a energia total gerada por cada inversor
    total_energy = {plant: sum(df_performance[plant]) for plant in df_performance.columns}

    # Criar DataFrame para a energia total gerada
    df_total_energy = pd.DataFrame(list(total_energy.items()), columns=['Usina', 'Energia Total (Wh)'])

    # Criar gráfico de barras com Plotly Express
    fig_bar_energy = px.bar(df_total_energy, x='Usina', y='Energia Total (Wh)', title='Energia Total Gerada por Usina')
    fig_bar_energy.update_layout(xaxis_title='Usina', yaxis_title='Energia Total (Wh)', legend_title_text='Usina')

    # Exibir o gráfico de barras no Streamlit
    st.title('Energia Total Gerada por Usina')
    st.plotly_chart(fig_bar_energy, use_container_width=True)

def save_to_excel(data):
    df = pd.DataFrame(data)
    file_path = os.path.join('Relatorios', 'motivos.xlsx')
    if not os.path.exists('Relatorios'):
        os.makedirs('Relatorios')
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

def detalhamento():
    st.title('Detalhamento de Motivos')
    usina = st.selectbox('Usina', ['Usina 1', 'Usina 2', 'Usina 3'])
    tipo_equipamento = st.selectbox('Tipo de Equipamento', ['Inversor', 'SB'])
    identificador_equipamento = st.selectbox('Identificador do Equipamento', [
        '331', '332', '333',  # Usina 1
        '431', '432', '433',  # Usina 2
        '531', '532', '533'   # Usina 3
    ])
    motivo = st.selectbox('Motivo', ['Bom', 'Ruim'])
    motivo_detalhado = st.text_area('Motivo Detalhado')
    data = st.date_input('Data')

    if st.button('Salvar'):
        data = {
            'Usina': [usina],
            'Tipo Equipamento': [tipo_equipamento],
            'Identificador Equipamento': [identificador_equipamento],
            'Motivo': [motivo],
            'Motivo Detalhado': [motivo_detalhado],
            'Data': [data]
        }
        save_to_excel(data)
        st.success('Motivo salvo com sucesso!')

#####################
## Streamlit Geral ##
#####################

# Adicionar uma barra lateral
selected_usina = st.sidebar.selectbox('Selecione a Usina', ['Todas', 'Usina 1', 'Usina 2', 'Usina 3'])
if selected_usina == 'Todas':
    selected_usina = None

# Gerenciar navegação entre abas
if 'analise' not in st.session_state:
    st.session_state.analise = 'Real Time'

def navigate_to(analise):
    st.session_state.analise = analise
    st.rerun()

add_sidebar = st.sidebar.selectbox('Análises', ('Real Time', 'Resumo Usina', 'Detalhamento Inversores', 'Detalhamento SBs'), index=['Real Time', 'Resumo Usina', 'Detalhamento Inversores', 'Detalhamento SBs'].index(st.session_state.analise))

#################
## Real Time ##
#################

if add_sidebar == 'Real Time':
    st.title('Indicadores Real Time')
    # Adicione aqui o código para os indicadores em tempo real

    # Botões para navegação
    if st.button('Detalhamento Inversores'):
        navigate_to('Detalhamento Inversores')

    if st.button('Detalhamento SBs'):
        navigate_to('Detalhamento SBs')

#################
## Resumo Usina ##
#################

if add_sidebar == 'Resumo Usina':
    st.title('Resumo Usina')
    irradiancia(selected_usina)

#############################
## Detalhamento Inversores ##
#############################

if add_sidebar == 'Detalhamento Inversores':
    st.title('Detalhamento Inversores')
    performance(selected_usina)
    detalhamento()

#############################
## Detalhamento SBs ##
#############################

if add_sidebar == 'Detalhamento SBs':
    st.title('Detalhamento SBs')
    detalhamento()