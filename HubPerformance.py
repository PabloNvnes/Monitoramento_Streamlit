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
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Dados google sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1RfN90_ye1SrsEjRlrumaNAhuVllu2Ii_7n7YHt2uSZk"
SAMPLE_RANGE_NAME = "Página1!A:F"

###############
##  Funções  ## 
###############

def get_google_sheet_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("sheets", "v4", credentials=creds)
        return service
    except HttpError as err:
        print(err)
        return None

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

def irradiancia(selected_usina=None, selected_date=None):

    # Lista de usinas fictícias com suas coordenadas
    plants = [
        {"plant": "Usina 1", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo"},
        {"plant": "Usina 2", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo"},
        {"plant": "Usina 3", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus"}
    ]

    if selected_usina:
        plants = [plant for plant in plants if plant["plant"] == selected_usina]

    # Obter dados de irradiância solar para as últimas 24 horas ou para um dia específico
    irradiance_data = {plant["plant"]: [] for plant in plants}
    time_data = []
    if selected_date:
        current_time = datetime.combine(selected_date, datetime.min.time()).replace(tzinfo=pytz.utc)
        for hour in range(24):
            time_point = current_time + timedelta(hours=hour)
            time_data.append(time_point)
            for plant in plants:
                timezone = pytz.timezone(plant["timezone"])
                local_time = time_point.astimezone(timezone)
                irradiance = get_solar_irradiance(plant["lat"], plant["lon"], local_time)
                irradiance_data[plant["plant"]].append(irradiance)
    else:
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

def load_detalhamentos(selected_usina=None, selected_date=None):
    service = get_google_sheet_service()
    if not service:
        return pd.DataFrame()

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    values = result.get("values", [])

    if not values:
        return pd.DataFrame()

    df = pd.DataFrame(values[1:], columns=values[0])
    df['data'] = pd.to_datetime(df['data'])

    if selected_usina:
        df = df[df['usina'] == selected_usina]
    if selected_date:
        df = df[df['data'].dt.date == selected_date]

    return df

def save_to_google_sheets(data):
    service = get_google_sheet_service()
    if not service:
        return

    sheet = service.spreadsheets()
    sheet.values().append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [data]}
    ).execute()

def performance(selected_inversor=None, selected_usina=None):
    # Lista de inversores fictícios com suas coordenadas
    inverters = [
        {"inverter": "331", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo", "usina": "Usina 1"},
        {"inverter": "332", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo", "usina": "Usina 1"},
        {"inverter": "333", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo", "usina": "Usina 1"},
        {"inverter": "431", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo", "usina": "Usina 2"},
        {"inverter": "432", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo", "usina": "Usina 2"},
        {"inverter": "433", "lat": -15.7942, "lon": -47.8822, "timezone": "America/Sao_Paulo", "usina": "Usina 2"},
        {"inverter": "531", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus", "usina": "Usina 3"},
        {"inverter": "532", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus", "usina": "Usina 3"},
        {"inverter": "533", "lat": -3.1190, "lon": -60.0217, "timezone": "America/Manaus", "usina": "Usina 3"}
    ]

    if selected_usina:
        inverters = [inverter for inverter in inverters if inverter["usina"] == selected_usina]

    if selected_inversor and selected_inversor != 'Todos Inversores':
        inverters = [inverter for inverter in inverters if inverter["inverter"] == selected_inversor]

    # Obter dados de irradiância solar para as últimas 24 horas para cada inversor a cada 5 minutos
    performance_data = {inverter["inverter"]: [] for inverter in inverters}
    time_data = []
    current_time = datetime.now(pytz.utc)
    for minute in range(0, 24 * 60, 5):
        time_point = current_time - timedelta(minutes=minute)
        time_data.append(time_point)
        for inverter in inverters:
            timezone = pytz.timezone(inverter["timezone"])
            local_time = time_point.astimezone(timezone)
            irradiance = get_solar_irradiance(inverter["lat"], inverter["lon"], local_time)
            performance = calculate_inverter_performance(irradiance)
            # Simular problemas nos inversores
            if random.random() < 0.05:  # 5% de chance de problema
                performance *= random.uniform(0.5, 0.9)  # Reduzir performance entre 10% e 50%
            performance_data[inverter["inverter"]].append(performance)

    # Criar DataFrame para facilitar a manipulação dos dados
    df_performance = pd.DataFrame(performance_data, index=time_data)

    # Inverter os dados para que o tempo esteja em ordem crescente
    df_performance = df_performance.iloc[::-1]

    # Criar gráfico de linhas com Plotly Express
    fig_performance = px.line(df_performance, x=df_performance.index, y=df_performance.columns, labels={'value': 'Performance do Inversor (W)', 'index': 'Hora'}, title='Performance do Inversor Solar a Cada 5 Minutos')
    fig_performance.update_layout(xaxis_title='Hora', yaxis_title='Performance do Inversor (W)', legend_title_text='Inversor')

    # Exibir o gráfico de linhas no Streamlit
    st.title('Performance do Inversor Solar a Cada 5 Minutos')
    st.plotly_chart(fig_performance, use_container_width=True)

    # Calcular a energia total gerada por cada inversor
    total_energy = {inverter: sum(df_performance[inverter]) for inverter in df_performance.columns}

    # Criar DataFrame para a energia total gerada
    df_total_energy = pd.DataFrame(list(total_energy.items()), columns=['Inversor', 'Energia Total (Wh)'])

    # Criar gráfico de barras com Plotly Express
    fig_bar_energy = px.bar(df_total_energy, x='Inversor', y='Energia Total (Wh)', title='Energia Total Gerada por Inversor')
    fig_bar_energy.update_layout(xaxis_title='Inversor', yaxis_title='Energia Total (Wh)', legend_title_text='Inversor', xaxis_type='category')

    # Exibir o gráfico de barras no Streamlit
    st.title('Energia Total Gerada por Inversor')
    st.plotly_chart(fig_bar_energy, use_container_width=True)

    # Gerar dados para SBs
    sb_performance_data = {}
    for inverter in inverters:
        for sb_index in range(1, 7):
            sb_id = f"{inverter['inverter']}_SB{sb_index}"
            sb_performance_data[sb_id] = [value / 6 for value in performance_data[inverter["inverter"]]]

    # Criar DataFrame para facilitar a manipulação dos dados das SBs
    df_sb_performance = pd.DataFrame(sb_performance_data, index=time_data)

    # Inverter os dados para que o tempo esteja em ordem crescente
    df_sb_performance = df_sb_performance.iloc[::-1]

    # Criar gráfico de linhas com Plotly Express para SBs
    fig_sb_performance = px.line(df_sb_performance, x=df_sb_performance.index, y=df_sb_performance.columns, labels={'value': 'Performance da SB (W)', 'index': 'Hora'}, title='Performance das SBs a Cada 5 Minutos')
    fig_sb_performance.update_layout(xaxis_title='Hora', yaxis_title='Performance da SB (W)', legend_title_text='SB')

    # Exibir o gráfico de linhas no Streamlit
    st.title('Performance das SBs a Cada 5 Minutos')
    st.plotly_chart(fig_sb_performance, use_container_width=True)

    # Calcular a energia total gerada por cada SB
    total_sb_energy = {sb: sum(df_sb_performance[sb]) for sb in df_sb_performance.columns}

    # Criar DataFrame para a energia total gerada das SBs
    df_total_sb_energy = pd.DataFrame(list(total_sb_energy.items()), columns=['SB', 'Energia Total (Wh)'])

    # Criar gráfico de barras com Plotly Express para SBs
    fig_bar_sb_energy = px.bar(df_total_sb_energy, x='SB', y='Energia Total (Wh)', title='Energia Total Gerada por SB')
    fig_bar_sb_energy.update_layout(xaxis_title='SB', yaxis_title='Energia Total (Wh)', legend_title_text='SB', xaxis_type='category')

    # Exibir o gráfico de barras no Streamlit
    st.title('Energia Total Gerada por SB')
    st.plotly_chart(fig_bar_sb_energy, use_container_width=True)

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
        data = [usina, tipo_equipamento, identificador_equipamento, motivo, motivo_detalhado, str(data)]
        save_to_google_sheets(data)
        st.success('Motivo salvo com sucesso!')

def navigate_to(analise):
    st.session_state.analise = analise
    st.rerun()

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

add_sidebar = st.sidebar.selectbox('Análises', ('Real Time', 'Resumo Usina', 'Detalhamento Produção de Energia'), index=['Real Time', 'Resumo Usina', 'Detalhamento Produção de Energia'].index(st.session_state.analise))

#################
## Real Time ##
#################

if add_sidebar == 'Real Time':
    st.title('Indicadores Real Time')
    # Adicione aqui o código para os indicadores em tempo real

    column1, column2, column3 = st.columns(3)

    with column1:
        producao_energia_atual = 1000  # valor fictício
        producao_energia_meta = 1100  # meta fictícia
        st.metric('Produção de Energia', f'{producao_energia_atual} kWh', f'{producao_energia_atual - producao_energia_meta} kWh')
        st.markdown(f"<span style='color: gray;'>Meta: {producao_energia_meta} kWh</span>", unsafe_allow_html=True)

    with column2:
        irradiancia_solar_atual = 1000  # valor fictício
        irradiancia_solar_meta = 1050  # meta fictícia
        st.metric('Irradiância Solar', f'{irradiancia_solar_atual} W/m²', f'{irradiancia_solar_atual - irradiancia_solar_meta} W/m²')
        st.markdown(f"<span style='color: gray;'>Meta: {irradiancia_solar_meta} W/m²</span>", unsafe_allow_html=True)

    with column3:  
        performance_inversor_atual = 1000  # valor fictício
        performance_inversor_meta = 1150  # meta fictícia
        st.metric('Performance do Inversor', f'{performance_inversor_atual} W', f'{performance_inversor_atual - performance_inversor_meta} W')
        st.markdown(f"<span style='color: gray;'>Meta: {performance_inversor_meta} W</span>", unsafe_allow_html=True)
        
    # Botões para navegação
    if st.button('Detalhamento Produção de Energia'):
        navigate_to('Detalhamento Produção de Energia')

#################
## Resumo Usina ##
#################

if add_sidebar == 'Resumo Usina':
    st.title('Resumo Usina')
    selected_date = st.date_input('Selecione a Data')
    irradiancia(selected_usina, selected_date)
    df_detalhamentos = load_detalhamentos(selected_usina, selected_date)
    st.title('Detalhamentos de Motivos')
    st.dataframe(df_detalhamentos)

#############################
## Detalhamento Produção de Energia ##
#############################

if add_sidebar == 'Detalhamento Produção de Energia':
    st.title('Detalhamento Produção de Energia')
    inversores_opcoes = ['Todos Inversores']
    if selected_usina == 'Usina 1':
        inversores_opcoes += ['331', '332', '333']
    elif selected_usina == 'Usina 2':
        inversores_opcoes += ['431', '432', '433']
    elif selected_usina == 'Usina 3':
        inversores_opcoes += ['531', '532', '533']
    else:
        inversores_opcoes += ['331', '332', '333', '431', '432', '433', '531', '532', '533']
    
    selected_inversor = st.selectbox('Selecione o Inversor', inversores_opcoes)
    performance(selected_inversor, selected_usina)
    detalhamento()