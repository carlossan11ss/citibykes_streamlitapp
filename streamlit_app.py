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
st.markdown("## ")
#columns
col11, col22 = st.columns(2)
with col22:
    st.image("citibike-image.jpg")
with col11:
    st.markdown(" ")
    st.markdown(    """
                    Integrantes:
                    - Federico Higuera
                    - Carlos Sánchez
                    - Cristian Ospina
                    
                    """)

st.markdown("## ")

col1, inter_cols_pace, col2 = st.columns((2, 8, 2))
with inter_cols_pace:
    st.markdown('## Visualizaciones interactivas')

# Cargar datos
@st.cache
def load_and_proccess_data():
    files =  sorted(glob('Parquets/part*')) # Lista de archivos

    data = pd.read_parquet(files[0]) # Cargamos el primer archivo
    for f in files[1:]:
        data = pd.concat([data, pd.read_parquet(f)]) # Concatenamos los archivos con el primer archivo

    ## Preprocesamiento de datos

    data['DATE'] = pd.to_datetime(data['DATE'])  # Convertirmos la fecha a su tipo de dato

    data = data[['tripduration', 'starttime', 'stoptime',
       'start_bike_station_id','start_bike_station_name', 'start_bike_station_latitude','start_bike_station_longitude',
       'end_bike_station_id','end_bike_station_name', 'end_bike_station_latitude', 'end_bike_station_longitude',
       'bikeid', 'usertype', 'birth_year','gender',
       'end_date', 'end_time','POI_NAME',
       'Weather_Station', 'NAME', 'LATITUDE', 'LONGITUDE',
       'ELEVATION', 'DATE', 'PRCP',
       'TMAX', 'TMIN', 'TAVG',
       'Month', 'Year']] # Seleccionamos las columnas que nos interesan

    data['tripminutes'] = data.tripduration/60 # Creamos una columna con la duración del viaje en minutos

    data['Semana'] = data.DATE.dt.isocalendar().week # Creamos una columna con el número de la semana
 
    data['genero'] = data.gender.replace({0:'Indefinido', 1:'Masculino', 2:'Femenino'}) # Creamos una columna con el género en texto

    data['Edad'] = pd.to_datetime(data['starttime']).dt.year - data['birth_year'] # Creamos una columna con la edad de los usuarios

    return data
data = load_and_proccess_data()

st.markdown('### Cantidad de viajes en bicicleta por tipo de usuario y por género, Con filtro de edades')

st.caption('FILTROS')

unused1, intercolspace, unused2 = st.columns((1, 8, 1))
with intercolspace:
    edad_input1 = st.slider('Edad (Años)', min_value=data['Edad'].min(), max_value=data['Edad'].max(),
                                        value=(data['Edad'].min(),data['Edad'].max()), step=1)

input1_, input2_ = st.columns((2,3))
with input1_:
    genero_input_ = st.multiselect('Género', data.genero.unique(), default=data.genero.unique(), key='genero1')
with input2_:
    tipo_usuario_input_ = st.multiselect('Tipo de Usuario', data.usertype.unique(), default=data.usertype.unique(), key='tipo_usuario1')




#Filtrar datos con los filtros del usuario

filtered_data_plot1 = data[(data['Edad'] >= edad_input1[0]) &
                           (data['Edad'] <= edad_input1[1]) &
                           (data['genero'].isin(genero_input_)) &
                           (data['usertype'].isin(tipo_usuario_input_))]


#Graficar

fig1 = px.histogram(filtered_data_plot1, x='usertype', color='genero',barmode='group')
fig1.update_xaxes(title_text='Tipo de Usuario')
fig1.update_yaxes(title_text='Cantidad de Viajes')
st.plotly_chart(fig1)

#Texto complementario
"""En esta gráfica podemos ver de qué género son los usuarios de cada tipo, también podemos determinar que
 tipo de usuario utiliza más los servicios de Citibikes"""

st.markdown('### Mapa de la densidad de los viajes en bicicleta según las características del usuario')
st.caption('FILTROS')

# Recolectar input del usuario
input_1, input_2 = st.columns((3,4))
with input_1:
    edad_input = st.slider('Edad (Años)', min_value=data['Edad'].min(), max_value=data['Edad'].max(), value=(24,39), step=1)
with input_2:
    tripduration_input = st.slider('Duración del viaje en minutos',
                                    min_value=int(data['tripminutes'].min()), max_value=1500,
                                    value=(int(data['tripminutes'].min()),1500), step=5)
input1, input2 = st.columns((2,3))
with input1:
    genero_input = st.multiselect('Género', data.genero.unique(), default=data.genero.unique(), key='genero2')
with input2:
    tipo_usuario_input = st.multiselect('Tipo de Usuario', data.usertype.unique(), default=data.usertype.unique(), key='tipo_usuario2')


# Crear dataset filtrado por edad
filtered_data_maps = data[ (data['Edad'] >= edad_input[0]) &
                           (data['Edad'] <= edad_input[1]) &
                           (data['tripminutes'] >= tripduration_input[0]) &
                           (data['tripminutes'] <= tripduration_input[1]) &
                           (data['genero'].isin(genero_input)) &
                           (data['usertype'].isin(tipo_usuario_input))
                         ]

if filtered_data_maps.shape[0] != 0: 
    # Calcular el centro del mapa
    mean_lat = filtered_data_maps['start_bike_station_latitude'].mean()
    mean_lon = filtered_data_maps['start_bike_station_longitude'].mean()

    # Crear mapa
    m = folium.Map(location=[mean_lat, mean_lon], zoom_start=12)

    # add heatmap to map
    HeatMap(data = filtered_data_maps[['start_bike_station_latitude','start_bike_station_longitude']].values.tolist(),
                    radius=12).add_to(m)


    st.markdown('# ')

    st_map = st_folium(m, width=700, height=450)
    " "
    " "
    """Acá podemos ver la utilización, en términos de número de viajes hechos, de los usuarios de Citibikes.
       Los filtros permiten saber en qué parte de la ciudad determinado grupo de usuarios
    hace más uso de los servicios de Citibikes"""
else:
    st.warning('No hay datos con los filtros seleccionados')