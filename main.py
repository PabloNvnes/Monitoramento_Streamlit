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

from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Obter dados de irradiância solar para as últimas 24 horas
irradiance_data = []
time_data = []
current_time = datetime.now(timezone)
for hour in range(24):
    time_point = current_time - timedelta(hours=hour)
    irradiance = get_solar_irradiance(lat, lon, time_point)
    irradiance_data.append(irradiance)
    time_data.append(time_point)

# Inverter os dados para que o tempo esteja em ordem crescente
irradiance_data.reverse()
time_data.reverse()

# Criar o gráfico
plt.figure(figsize=(10, 5))
plt.plot(time_data, irradiance_data, marker='o')
plt.xlabel('Hora')
plt.ylabel('Irradiância Solar (W/m²)')
plt.title('Irradiância Solar nas Últimas 24 Horas em São Paulo')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Exibir o gráfico no Streamlit
st.title('Gráfico de Irradiância Solar nas Últimas 24 Horas')
st.pyplot(plt)