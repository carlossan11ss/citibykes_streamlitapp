# Importar librerias
import streamlit as st
import pandas as pd
import plotly.express as px
from glob import glob
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

#Configuración inicial de la página
st.set_page_config(page_title='CityBikes',
                 layout='centered')



st.title('Exploración de datos de CityBikes')
st.subheader('Visualizaciones interactivas')

# Cargar datos
@st.cache
def load_and_proccess_data():
    files =  sorted(glob('Parquets/part*')) # Lista de archivos

    data = pd.read_parquet(files[0]) # Cargamos el primer archivo
    for f in files[1:]:
        data = pd.concat([data, pd.read_parquet(f)]) # Concatenamos los archivos con el primer archivo

    data['DATE'] = pd.to_datetime(data['DATE'])  # Convertirmos la fecha a su tipo de dato

    data = data[['tripduration', 'starttime', 'stoptime',
       'start_bike_station_id','start_bike_station_name', 'start_bike_station_latitude','start_bike_station_longitude',
       'end_bike_station_id','end_bike_station_name', 'end_bike_station_latitude', 'end_bike_station_longitude',
       'bikeid', 'usertype', 'birth_year','gender',
       'end_date', 'end_time','POI_NAME',
       'Weather_Station', 'NAME', 'LATITUDE', 'LONGITUDE',
       'ELEVATION', 'DATE', 'PRCP',
       'TMAX', 'TMIN', 'TAVG',
       'Month', 'Year']]
    
    data['Semana'] = data.DATE.dt.isocalendar().week

    data['genero'] = data.gender.replace({0:'Indefinido', 1:'Masculino', 2:'Femenino'})

    data['Edad'] = pd.to_datetime(data['starttime']).dt.year - data['birth_year']

    return data

data = load_and_proccess_data()



fig1 = px.histogram(data, x='usertype', color='genero',barmode='group')
fig1.update_xaxes(title_text='Tipo de Usuario')
fig1.update_yaxes(title_text='Cantidad de Viajes')
st.plotly_chart(fig1)


fig2 = px.histogram(data, x='genero', color='usertype',barmode='group')
fig2.update_yaxes(title_text='Cantidad de Viajes')
st.plotly_chart(fig2)


edad_input = st.slider('Edad', min_value=0, max_value=100, value=(0,100), step=1)


# Crear dataset filtrado por edad
filtered_data_maps = data[ (data['Edad'] >= edad_input[0]) & (data['Edad'] <= edad_input[1])]

# Calcular el centro del mapa
mean_lat = filtered_data_maps['start_bike_station_latitude'].mean()
mean_lon = filtered_data_maps['start_bike_station_longitude'].mean()

# Crear mapa
m = folium.Map(location=[mean_lat, mean_lon], zoom_start=12)

# add heatmap to map
HeatMap(data = filtered_data_maps[['start_bike_station_latitude','start_bike_station_longitude']].values.tolist(),
                 radius=12).add_to(m)

st_map = st_folium(m, width=700, height=450)