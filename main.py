# Importações
import streamlit as st
from datetime import datetime
import pytz
from pysolar.solar import get_altitude
from pysolar.radiation import get_radiation_direct

# Função para obter dados de irradiância solar
def get_solar_irradiance(lat, lon, date_time):
    altitude = get_altitude(lat, lon, date_time)
    if altitude > 0:
        irradiance = get_radiation_direct(date_time, altitude)
    else:
        irradiance = 0
    return irradiance

# Coordenadas da localização desejada
lat, lon = -23.5505, -46.6333  # Coordenadas de São Paulo
timezone = pytz.timezone('America/Sao_Paulo')
date_time = datetime.now(timezone)

# Obter dados de irradiância solar
irradiance = get_solar_irradiance(lat, lon, date_time)

# Exibir dados no Streamlit
st.title('Dados de Irradiância Solar em Tempo Real')
st.write(f"Irradiância solar atual em São Paulo: {irradiance} W/m²")