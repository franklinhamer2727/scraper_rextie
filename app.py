import pandas as pd
import streamlit as st
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📈 Evolución del Tipo de Cambio - Rextie Scraper")

# Ruta al archivo CSV
csv_file = "data/rextie_dolar.csv"

# Definimos colores por fuente
FUENTE_COLORS = {
    "Kambista": "blue",
    "Tkambio": "green",
    "Rextie": "red",  # Añadir más fuentes según sea necesario
}

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_file)
    # Asegurarse de que 'fecha' y 'hora' están en el formato adecuado
    df['datetime'] = pd.to_datetime(df['fecha'] + ' ' + df['hora'], format='%Y-%m-%d %H:%M:%S')
    df = df.sort_values('datetime')
    return df

# Cargar los datos
df = load_data()

# Mostrar tabla reciente
st.subheader("📋 Últimos datos")
st.dataframe(df.tail(10), use_container_width=True)

# Gráfica de líneas para compra y venta
st.subheader("📊 Evolución del Tipo de Cambio")

# 1. Gráfico de líneas
fig_line = px.line(
    df,
    x="datetime",
    y=["compra", "venta"],
    color="fuente",  # Mostrar los datos separados por fuente (empresa)
    markers=True,
    labels={"datetime": "Hora", "value": "Precio (S/)", "variable": "Tipo de Cambio"},
    title="Evolución de Compra y Venta por Fuente",
    color_discrete_map=FUENTE_COLORS  # Asignamos colores personalizados
)

# Modificamos los iconos para los puntos de "compra" y "venta"
fig_line.update_traces(marker=dict(symbol="circle-open"), selector=dict(name="compra"))
fig_line.update_traces(marker=dict(symbol="star-open"), selector=dict(name="venta"))

fig_line.update_layout(
    xaxis_title="Hora",
    yaxis_title="Precio (S/)",
    height=500,
    xaxis=dict(tickformat='%H:%M:%S'),  # Para mostrar las horas en el formato adecuado
)

st.plotly_chart(fig_line, use_container_width=True)

# 2. Gráfico de velas (Candlestick)
fig_candlestick = go.Figure(data=[go.Candlestick(
    x=df['datetime'],
    open=df['compra'],  # Se puede usar "compra" como apertura
    high=df[['compra', 'venta']].max(axis=1),  # Máximo entre compra y venta
    low=df[['compra', 'venta']].min(axis=1),   # Mínimo entre compra y venta
    close=df['venta'],  # Se puede usar "venta" como cierre
    increasing_line_color='green',
    decreasing_line_color='red',
)])
fig_candlestick.update_layout(
    title="Gráfico de Velas de Compra y Venta",
    xaxis_title="Hora",
    yaxis_title="Precio (S/)",
    xaxis_rangeslider_visible=False,
    height=500
)
st.plotly_chart(fig_candlestick, use_container_width=True)

# 3. Gráfico de dispersión (Scatter Plot)
fig_scatter = px.scatter(
    df,
    x="compra",
    y="venta",
    color="fuente",  # Relación entre compra y venta por fuente
    labels={"compra": "Precio de Compra (S/)", "venta": "Precio de Venta (S/)", "fuente": "Fuente"},
    title="Relación entre Precio de Compra y Venta por Fuente",
    color_discrete_map=FUENTE_COLORS  # Asignamos colores personalizados
)
st.plotly_chart(fig_scatter, use_container_width=True)

# 4. Gráfico de histograma (Histograma de Precios de Compra y Venta)
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(
    x=df['compra'],
    name='Precio de Compra',
    opacity=0.75,
    marker=dict(color='blue'),
    xbins=dict(start=df['compra'].min(), end=df['compra'].max(), size=0.01),
))
fig_hist.add_trace(go.Histogram(
    x=df['venta'],
    name='Precio de Venta',
    opacity=0.75,
    marker=dict(color='orange'),
    xbins=dict(start=df['venta'].min(), end=df['venta'].max(), size=0.01),
))

fig_hist.update_layout(
    barmode='overlay',
    title="Distribución de Precios de Compra y Venta",
    xaxis_title="Precio (S/)",
    yaxis_title="Frecuencia",
    height=500
)
st.plotly_chart(fig_hist, use_container_width=True)

# 5. Gráfico de evolución del tipo de cambio por empresa (fuente)
st.subheader("📊 Evolución del Tipo de Cambio por Empresa")

# Auto-refresh en el dashboard cada 60 segundos
time.sleep(60)  # Pausa de 60 segundos antes de hacer el refresh

st.rerun() # Recarga el script de Streamlit
