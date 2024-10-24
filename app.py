import streamlit as st
from statsbombpy import sb
from fpdf import FPDF
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd
from fpdf import FPDF
import base64
from PIL import Image, ImageOps, ImageDraw
import io
import base64

def hacer_imagen_redonda(imagen):
    imagen = imagen.convert("RGBA")
    mascara = Image.new("L", imagen.size, 0)
    dibujar = ImageDraw.Draw(mascara)
    dibujar.ellipse((0, 0) + imagen.size, fill=255)
    imagen.putalpha(mascara)
    return imagen

imagen = Image.open("s_NQaIez_400x400.jpg")
imagen_redonda = hacer_imagen_redonda(imagen)
imagen_redonda = imagen_redonda.resize((100, 100))

buf = io.BytesIO()
imagen_redonda.save(buf, format="PNG")  
imagen_bytes = buf.getvalue()

imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")
st.sidebar.markdown(
    f"""
    <div style='display: flex; justify-content: center;'>
        <img src='data:image/png;base64,{imagen_base64}' style='border-radius: 50%; width: 100px; height: 100px;'/>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("<h3 style='text-align: center; color: black;'>ITAM Sport Analytics Conference</h3>", unsafe_allow_html=True)
st.sidebar.write("- - - - - - - - - - - ")
st.sidebar.markdown("<h1 style='text-align: center; color: black;'>Sheplays Analytics</h1>", unsafe_allow_html=True)
st.sidebar.write("""
    El equipo que elijas será analizado en el 1er tiempo para entender cómo está siendo atacado ofensivamente, con el objetivo de identificar cambios tácticos en el equipo para el 2do tiempo.
""")

st.title("Herramienta de análisis sobre la peligrosidad de las zonas conquistadas VS el parado táctico")
torneo_seleccionado = "Euro 2024"
st.sidebar.subheader(f"Torneo: {torneo_seleccionado}")
torneo_id = 55  
partidos_torneo = sb.matches(competition_id=torneo_id, season_id=282)

partidos_dict = {}
for index, row in partidos_torneo.iterrows():
    stage_name = row['competition_stage']['name'] if row['competition_stage'] and 'name' in row['competition_stage'] else 'Desconocido'
    partido_nombre = f"{row['home_team']} vs {row['away_team']} ({stage_name})"
    partidos_dict[partido_nombre] = row['match_id']

partido_seleccionado = st.sidebar.selectbox("Selecciona el encuentro:", list(partidos_dict.keys()))
partido_id = partidos_dict[partido_seleccionado]
st.sidebar.write(f"Has seleccionado el encuentro: **{partido_seleccionado}** con Match ID: **{partido_id}**")
eventos = sb.events(match_id=partido_id)


equipo_local = eventos['team'].iloc[0]['name'] if isinstance(eventos['team'].iloc[0], dict) else eventos['team'].iloc[0]
equipo_visitante = eventos['team'].iloc[1]['name'] if isinstance(eventos['team'].iloc[1], dict) else eventos['team'].iloc[1]

equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo a analizar:", [equipo_local, equipo_visitante])
st.sidebar.write(f"Has seleccionado analizar al equipo: **{equipo_seleccionado}**")
eventos_equipo = eventos[eventos['team'] == equipo_seleccionado]



#------------Consideraciones iniciales inicio:
#------------Consideraciones iniciales inicio:
#------------Consideraciones iniciales inicio:


st.header("Consideraciones iniciales", divider=True)
st.markdown("""
Esta aplicación te servirá como apoyo para analizar lo ocurrido en los encuentros de la Euro 2024,
utilizando los datos públicos de StatsBomb. La información se te presentará de la siguiente forma:

- **Datos iniciales del encuentro:** Jugadores de ambas escuadras, cambios, formación inicial y marcador al medio tiempo.
- **Análisis de cambios tácticos en el primer tiempo - Euro 2024:** En aquellos encuentros donde se realizaron cambios tácticos en la formación, estos serán desglosados en esta sección.
- **Considerar realizar ajustes tácticos en la siguiente área del terreno de juego:** En esta sección encontrarás la recomendación de acuerdo con el análisis, donde se debió poner atención en realizar ajustes tácticos en la formación.
- **Resumen de la actividad ofensiva del contrincante en el segundo tiempo:** En esta parte encontrarás el comportamiento en el tiempo restante del segundo tiempo para contrastar las decisiones que hubieras tomado en lugar del DT, y si estas coinciden con lo ocurrido en el encuentro, así como validar la táctica del DT en cuestión.

**Nota importante:** Los gráficos están diseñados para hacer el análisis de cómo el equipo está siendo atacado. Verás las formaciones invertidas, ya que de esta forma se facilita la lectura de los gráficos para entender que desde esa perspectiva el equipo está siendo atacado.
""")

st.subheader('Descripcion de los graficos.', divider=True)
# Descripción para el gráfico 1
st.markdown("""   
#### Ganancia de Metros Hacia la Portería

El gráfico muestra un mapa de calor que ilustra las zonas donde el equipo contrincante logró avanzar hacia la portería. Las áreas más oscuras representan zonas donde hubo mayor cantidad de metros ganados, indicando las áreas más peligrosas para el equipo seleccionado. El gráfico también incluye una barra de colores para mostrar diferentes rangos de metros ganados.
            
Este gráfico muestra la ganancia de metros hacia la portería rival. Se utiliza la columna `location` para la posición inicial y la columna `pass_end_location` para la posición final. Solo se considera la ganancia si el evento avanzó en dirección a la portería.
""")

# Ecuación para el gráfico 1
st.latex(r'''
\text{ganancia\_metros} = \sqrt{(x_{\text{final}} - x_{\text{inicio}})^2 + (y_{\text{final}} - y_{\text{inicio}})^2}
''')

st.image("ganancia_metros.png")


# Descripción para el gráfico 2
st.markdown("""
#### Zonas de Peligro y Direcciones del Ataque
            
Este gráfico busca representar cómo se distribuyeron los ataques del equipo contrario. Las zonas con mayor densidad de ataques, marcadas por el mapa de calor, indican las áreas donde el equipo rival pudo generar más peligro. Las líneas y etiquetas de distancia añaden una capa de detalle que permite interpretar mejor la relación entre el ataque y la estructura del campo.
            
Este gráfico representa la densidad de los eventos ofensivos en función de su ubicación final, usando las columnas `location` y `pass_end_location` para determinar la dirección del ataque.
""")

# Ecuación para el gráfico 2
st.latex(r'''
\text{dirección\_ataque} = \text{kde}(x_{\text{final}}, y_{\text{final}})
''')
st.markdown("La densidad se calcula con la función de densidad de kernel (kde), mostrando las áreas de mayor actividad ofensiva.")

st.image("zonas_de_peligro.png")

# Descripción para el gráfico 3
st.markdown("""
#### Peligrosidad de las Zonas Conquistadas (Expected Goals)
            
Este análisis es útil para identificar las zonas del campo donde se originan los tiros más peligrosos, basados en los valores de xG. Específicamente, se puede observar si los cambios tácticos influyeron en la peligrosidad de las áreas de ataque del equipo o de su oponente. Las líneas de medición y etiquetas agregan contexto espacial, ayudando a comprender la relación entre las ubicaciones de los tiros y el campo.
            
Este gráfico muestra las zonas más peligrosas basadas en la métrica de Expected Goals (**xG**). Utiliza las columnas `shot_end_location` y `shot_statsbomb_xg` para determinar la ubicación y la peligrosidad de los tiros.
""")

# Ecuación para el gráfico 3
st.latex(r'''
\text{peligrosidad} = \sum (\text{xG}_{\text{ubicacion}} \times \text{frecuencia})
''')
st.markdown("La peligrosidad de una zona se define como la suma de los valores de **xG** de los tiros desde esa ubicación.")

st.image("zonas_conquistadas.png")

st.markdown("""
            
A continuación aparecerán todos los encuentros de la Euro 2024, para identificar qué escuadras realizaron cambios tácticos en la formación a lo largo del primer tiempo, con la finalidad de identificar cuáles encuentros tendrán en esta app un desglose de su táctica en la formación del primer tiempo:
""")

with st.spinner('Cargando los datos de cambios tácticos desde el archivo...'):
    df_cambios_tacticos = pd.read_csv('cambios_tacticos_euro_2024.csv')

st.dataframe(df_cambios_tacticos)

# Opción para descargar los resultados como CSV
st.download_button(
    label="Descargar CSV",
    data=df_cambios_tacticos.to_csv(index=False).encode('utf-8'),
    file_name='cambios_tacticos_euro_2024.csv',
    mime='text/csv'
)
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽  ")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ")
st.markdown("⚽ ⚽ ⚽ ")

#------------Consideraciones iniciales fin:
#------------Consideraciones iniciales fin:
#------------Consideraciones iniciales fin:


#-----------------------------(INICIO) -- RESUMEN 1 ------------------------------------------------------
#-----------------------------(INICIO) -- RESUMEN 1 ------------------------------------------------------
#-----------------------------(INICIO) -- RESUMEN 1 ------------------------------------------------------
#-----------------------------(INICIO) -- RESUMEN 1 ------------------------------------------------------
#-----------------------------(INICIO) -- RESUMEN 1 ------------------------------------------------------
#-----------------------------(INICIO) -- RESUMEN 1 ------------------------------------------------------


@st.cache_data
def cargar_eventos(partido_id):
    return sb.events(match_id=partido_id)

eventos = cargar_eventos(partido_id)
eventos_partido = eventos[eventos['period'] == 1]
equipos = eventos_partido['team'].unique()

if len(equipos) >= 2:
    jugadores_equipo1 = eventos_partido[eventos_partido['team'] == equipos[0]]['player'].unique()
    jugadores_equipo2 = eventos_partido[eventos_partido['team'] == equipos[1]]['player'].unique()

    cambios_equipo1 = eventos_partido[(eventos_partido['team'] == equipos[0]) & (eventos_partido['type'] == 'Substitution')]
    cambios_equipo2 = eventos_partido[(eventos_partido['team'] == equipos[1]) & (eventos_partido['type'] == 'Substitution')]

    st.header("")
    st.header("Datos iniciales del encuentro", divider=True)
    st.write("La informacion a continuacion nos ayudara a concocer que jugadores tuvieron oportunidad de disputar el encuentro, los cambios realizados por ambas escuadras, el minuto donde sucedieron los cambios, y los cambios tacticos en las formaciones durante el primer tiempo, asi como el marcador al medio tiempo.")
    st.subheader(f"**Equipos:** {equipos[0]} vs {equipos[1]}")
        
    col1, col2 = st.columns(2)
    jugadores_equipo1 = [jugador for jugador in jugadores_equipo1 if pd.notna(jugador)]
    jugadores_equipo2 = [jugador for jugador in jugadores_equipo2 if pd.notna(jugador)]

    with col1:
        st.write(f"Jugadores del {equipos[0]} en el primer tiempo:")
        jugadores_equipo1_df = pd.DataFrame({'Jugadores': jugadores_equipo1})  
        st.table(jugadores_equipo1_df) 

    with col2:
        st.write(f"Jugadores del {equipos[1]} en el primer tiempo:")
        jugadores_equipo2_df = pd.DataFrame({'Jugadores': jugadores_equipo2})  
        st.table(jugadores_equipo2_df)  

    if not cambios_equipo1.empty:
        st.write(f"Cambios en el {equipos[0]} en el primer tiempo:")
        for index, row in cambios_equipo1.iterrows():
            st.write(f"- {row['player']} fue sustituido por {row['substitution_replacement']} al minuto {row['minute']}")
    else:
        st.write(f"No hubo cambios en el {equipos[0]} en el primer tiempo.")

    if not cambios_equipo2.empty:
        st.write(f"Cambios en el {equipos[1]} en el primer tiempo:")
        for index, row in cambios_equipo2.iterrows():
            st.write(f"- {row['player']} fue sustituido por {row['substitution_replacement']} al minuto {row['minute']}")
    else:
        st.write(f"No hubo cambios en el {equipos[1]} en el primer tiempo.")
else:
    st.write("No hay datos suficientes para mostrar información sobre este partido.")
    
def obtener_marcador_ht(match_id):
    eventos = sb.events(match_id=match_id)

    goles_local = eventos[(eventos['type'] == 'Shot') & 
                          (eventos['shot_outcome'] == 'Goal') & 
                          (eventos['period'] == 1) & 
                          (eventos['possession_team'] == eventos['possession_team'].iloc[0])]

    goles_visitante = eventos[(eventos['type'] == 'Shot') & 
                              (eventos['shot_outcome'] == 'Goal') & 
                              (eventos['period'] == 1) & 
                              (eventos['possession_team'] != eventos['possession_team'].iloc[0])]

    marcador_local_ht = len(goles_local)
    marcador_visitante_ht = len(goles_visitante)
    teams = eventos['team'].unique()
    home_team = teams[0]  
    away_team = teams[1]  

    st.subheader(f"Marcador al final del primer tiempo: {home_team} {marcador_local_ht} - {marcador_visitante_ht} {away_team}") 

def obtener_coordenadas_por_formacion(formacion):
    formaciones_dict = {
    433: [(20, 80), (40, 80), (60, 80),   # Delanteros
          (20, 60), (40, 60), (60, 60),   # Mediocampistas
          (10, 40), (30, 40), (50, 40), (70, 40), # Defensas
          (40, 20)],                      # Portero
    442: [(25, 80), (55, 80),             # Delanteros
          (10, 60), (30, 60), (50, 60), (70, 60), # Mediocampistas
          (10, 40), (30, 40), (50, 40), (70, 40), # Defensas
          (40, 20)],                      # Portero
    4231: [(40, 85),                      # Delantero (centro)
           (20, 70), (40, 70), (60, 70),  # Mediocampistas ofensivos (izquierda, centro, derecha)
           (30, 55), (50, 55),            # Mediocentros defensivos
           (15, 40), (35, 40), (55, 40), (75, 40),  # Defensas (laterales y centrales)
           (40, 20)],                      # Portero (centro)
    41212: [(30, 80), (50, 80),           # Delanteros (izquierda, derecha)
            (40, 70),                     # Mediocentro ofensivo (centro)
            (30, 60), (50, 60),           # Mediocentros (izquierda, derecha)
            (40, 50),                     # Mediocentro defensivo (centro)
            (20, 40), (60, 40),           # Laterales (izquierdo, derecho)
            (30, 40), (50, 40),           # Defensas centrales
            (40, 20)],                     # Portero (centro)
    3412: [(40, 85),                      # Delantero (centro)
           (30, 70), (50, 70),            # Mediocentros ofensivos (izquierdo y derecho)
           (40, 60),                      # Mediocentro defensivo (centro)
           (20, 65), (60, 65),            # Laterales (izquierdo y derecho)
           (20, 40), (40, 40), (60, 40),  # Defensas (líbero y centrales)
           (40, 20)],                      # Portero (centro)
    352: [(40, 80),                       # Delantero
          (30, 70), (50, 70),             # Mediocampistas ofensivos
          (40, 55), (40, 50),             # Laterales
          (20, 65), (60, 65),             # Defensas
          (40, 20)],                      # Portero
    3511: [(40, 80),                      # Delantero
           (30, 70), (50, 70),            # Mediocampistas ofensivos
           (40, 55),                      # Mediocentro defensivo
           (20, 65), (60, 65),            # Laterales
           (10, 40), (30, 40), (50, 40),  # Defensas
           (40, 20)],                     # Portero
    343: [(30, 85), (40, 85), (50, 85),   # Delanteros (izquierdo, central, derecho)
          (20, 65), (60, 65),             # Laterales (izquierdo y derecho)
          (30, 55), (50, 55),             # Mediocentros defensivos (izquierdo y derecho)
          (20, 40), (40, 40), (60, 40),   # Defensas (izquierdo, central, derecho)
          (40, 20)], 
    4222: [(35, 80), (45, 80),            # Delanteros (izquierdo y derecho)
           (25, 70), (55, 70),            # Mediocampistas ofensivos (izquierdo y derecho)
           (35, 60), (45, 60),            # Mediocentros defensivos (izquierdo y derecho)
           (20, 40), (60, 40),            # Defensas laterales (izquierdo y derecho)
           (30, 40), (50, 40),            # Defensas centrales (izquierdo y derecho)
           (40, 20)],                      # Portero (centro)
    4141: [(40, 80),                      # Delantero
           (30, 65), (50, 65),            # Mediocampistas ofensivos
           (40, 55),                      # Mediocentro defensivo
           (10, 40), (30, 40), (50, 40),  # Defensas
           (40, 20)],                     # Portero
     4411: [(40, 85),                      # Delantero (centro)
           (40, 70),                      # Mediapunta (centro)
           (20, 65), (60, 65),            # Mediocampistas laterales (izquierdo y derecho)
           (30, 65), (50, 65),            # Mediocentros (izquierdo y derecho)
           (20, 40), (60, 40),            # Defensas laterales (izquierdo y derecho)
           (30, 40), (50, 40),            # Defensas centrales
           (40, 20)],                      # Portero (centro)
    451: [(40, 80),                       # Delantero
          (30, 65), (50, 65), (30, 55), (50, 55),  # Mediocampistas ofensivos
          (40, 45),                      # Mediocentro defensivo
          (10, 40), (30, 40), (50, 40),  # Defensas
          (40, 20)],                      # Portero
    3421: [(40, 80),                      # Delantero (centro)
           (30, 70), (50, 70),            # Mediocentros ofensivos (izquierda y derecha)
           (20, 60), (60, 60),            # Carrileros (izquierdo y derecho)
           (30, 55), (50, 55),            # Mediocentros (izquierdo y derecho)
           (20, 40), (40, 40), (60, 40),  # Defensas (líbero y centrales)
           (40, 20)]                      # Portero
}
    return formaciones_dict.get(formacion, None)

eventos = sb.events(match_id=partido_id)
alineacion_inicial = eventos[(eventos['type'] == 'Starting XI') & (eventos['team'] == equipo_seleccionado)]

if not alineacion_inicial.empty:
    formacion_inicial = alineacion_inicial.iloc[0]['tactics']['formation']
    st.write(f"El equipo {equipo_seleccionado} comenzó con la formación {formacion_inicial}.", divider=True)

    posicion_coords = obtener_coordenadas_por_formacion(formacion_inicial)

    if posicion_coords:
        pitch = Pitch(pitch_type='statsbomb', line_color='black', pitch_color='#aaddaa')  
        fig, ax = pitch.draw(figsize=(10, 7))
        x_coords = [120 - pos[1] for pos in posicion_coords]  
        y_coords = [80 - pos[0] for pos in posicion_coords]   
        pitch.scatter(x_coords, y_coords, ax=ax, c='blue', s=300, edgecolors='black', linewidth=1.5)
        formacion_invertida = int(str(formacion_inicial)[::-1])
        ax.set_title(f"Formación inicial {formacion_inicial} - {equipo_seleccionado} --> formación invertida {formacion_invertida}", fontsize=15)
        st.pyplot(fig)
    else:
        st.write(f"No se encontró una formación predefinida para la formación {formacion_inicial}.")
else:
    st.write(f"No se pudo encontrar la alineación inicial para {equipo_seleccionado} en el partido {partido_id}.")


match_id = partido_id  
obtener_marcador_ht(match_id)

st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽  ")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ")
st.markdown("⚽ ⚽ ⚽ ")
#-----------------------------(FIN) -- RESUMEN 1 ------------------------------------------------------ 
#-----------------------------(FIN) -- RESUMEN 1 ------------------------------------------------------ 
#-----------------------------(FIN) -- RESUMEN 1 ------------------------------------------------------ 
#-----------------------------(FIN) -- RESUMEN 1 ------------------------------------------------------ 
#-----------------------------(FIN) -- RESUMEN 1 ------------------------------------------------------ 
#-----------------------------(FIN) -- RESUMEN 1 ------------------------------------------------------ 



#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(INICIO) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------

st.header("")
st.header("Análisis de Cambios Tácticos en el Primer Tiempo", divider=True)
st.write("Este desglose te ayudara a entender de mejor manera que cambios tacticos en la formacion, ocurrieron durante el primer tiempo, para entender mejor la evolucion del encuentro en el primer tiempo, considerar que no todos los equipos realizaron cambios en la formacion en el primer tiempo, revisar la tabla de consideraciones iniciales.")
st.markdown(
    "<h4 style='color: red;'>Los gráficos muestran cómo el equipo está siendo atacado, no cómo ataca.</h4>",
    unsafe_allow_html=True
)

def obtener_coordenadas_por_formacion(formacion):
    formaciones_dict = {
    433: [(20, 80), (40, 80), (60, 80),   # Delanteros
          (20, 60), (40, 60), (60, 60),   # Mediocampistas
          (10, 40), (30, 40), (50, 40), (70, 40), # Defensas
          (40, 20)],                      # Portero
    442: [(25, 80), (55, 80),             # Delanteros
          (10, 60), (30, 60), (50, 60), (70, 60), # Mediocampistas
          (10, 40), (30, 40), (50, 40), (70, 40), # Defensas
          (40, 20)],                      # Portero
    4231: [(40, 85),                      # Delantero (centro)
           (20, 70), (40, 70), (60, 70),  # Mediocampistas ofensivos (izquierda, centro, derecha)
           (30, 55), (50, 55),            # Mediocentros defensivos
           (15, 40), (35, 40), (55, 40), (75, 40),  # Defensas (laterales y centrales)
           (40, 20)],                      # Portero (centro)
    41212: [(30, 80), (50, 80),           # Delanteros (izquierda, derecha)
            (40, 70),                     # Mediocentro ofensivo (centro)
            (30, 60), (50, 60),           # Mediocentros (izquierda, derecha)
            (40, 50),                     # Mediocentro defensivo (centro)
            (20, 40), (60, 40),           # Laterales (izquierdo, derecho)
            (30, 40), (50, 40),           # Defensas centrales
            (40, 20)],                     # Portero (centro)
    3412: [(40, 85),                      # Delantero (centro)
           (30, 70), (50, 70),            # Mediocentros ofensivos (izquierdo y derecho)
           (40, 60),                      # Mediocentro defensivo (centro)
           (20, 65), (60, 65),            # Laterales (izquierdo y derecho)
           (20, 40), (40, 40), (60, 40),  # Defensas (líbero y centrales)
           (40, 20)],                      # Portero (centro)
    352: [(40, 80),                       # Delantero
          (30, 70), (50, 70),             # Mediocampistas ofensivos
          (40, 55), (40, 50),             # Laterales
          (20, 65), (60, 65),             # Defensas
          (40, 20)],                      # Portero
    3511: [(40, 80),                      # Delantero
           (30, 70), (50, 70),            # Mediocampistas ofensivos
           (40, 55),                      # Mediocentro defensivo
           (20, 65), (60, 65),            # Laterales
           (10, 40), (30, 40), (50, 40),  # Defensas
           (40, 20)],                     # Portero
    343: [(30, 85), (40, 85), (50, 85),   # Delanteros (izquierdo, central, derecho)
          (20, 65), (60, 65),             # Laterales (izquierdo y derecho)
          (30, 55), (50, 55),             # Mediocentros defensivos (izquierdo y derecho)
          (20, 40), (40, 40), (60, 40),   # Defensas (izquierdo, central, derecho)
          (40, 20)], 
    4222: [(35, 80), (45, 80),            # Delanteros (izquierdo y derecho)
           (25, 70), (55, 70),            # Mediocampistas ofensivos (izquierdo y derecho)
           (35, 60), (45, 60),            # Mediocentros defensivos (izquierdo y derecho)
           (20, 40), (60, 40),            # Defensas laterales (izquierdo y derecho)
           (30, 40), (50, 40),            # Defensas centrales (izquierdo y derecho)
           (40, 20)],                      # Portero (centro)
    4141: [(40, 80),                      # Delantero
           (30, 65), (50, 65),            # Mediocampistas ofensivos
           (40, 55),                      # Mediocentro defensivo
           (10, 40), (30, 40), (50, 40),  # Defensas
           (40, 20)],                     # Portero
     4411: [(40, 85),                      # Delantero (centro)
           (40, 70),                      # Mediapunta (centro)
           (20, 65), (60, 65),            # Mediocampistas laterales (izquierdo y derecho)
           (30, 65), (50, 65),            # Mediocentros (izquierdo y derecho)
           (20, 40), (60, 40),            # Defensas laterales (izquierdo y derecho)
           (30, 40), (50, 40),            # Defensas centrales
           (40, 20)],                      # Portero (centro)
    451: [(40, 80),                       # Delantero
          (30, 65), (50, 65), (30, 55), (50, 55),  # Mediocampistas ofensivos
          (40, 45),                      # Mediocentro defensivo
          (10, 40), (30, 40), (50, 40),  # Defensas
          (40, 20)],                      # Portero
    3421: [(40, 80),                      # Delantero (centro)
           (30, 70), (50, 70),            # Mediocentros ofensivos (izquierda y derecha)
           (20, 60), (60, 60),            # Carrileros (izquierdo y derecho)
           (30, 55), (50, 55),            # Mediocentros (izquierdo y derecho)
           (20, 40), (40, 40), (60, 40),  # Defensas (líbero y centrales)
           (40, 20)]                      # Portero
}
    return formaciones_dict.get(formacion, None)

eventos = sb.events(match_id=partido_id)

cambios_tacticos = eventos[(eventos['type'] == 'Tactical Shift') & 
                           (eventos['period'] == 1) & 
                           (eventos['team'] == equipo_seleccionado)]

graficos_resumen = 0

for index, row in cambios_tacticos.iterrows():
    minuto = row['minute']  # Minuto del cambio táctico
    formacion = row['tactics']['formation']  # Formación táctica en ese momento
    alineacion = row['tactics']['lineup']  # Alineación de jugadores en esa formación
    
    #if formacion == ultima_formacion:
    #    continue
    
    ultima_formacion = formacion
    formacion_inver = int(str(ultima_formacion)[::-1])
    st.subheader(f"Minuto {minuto}: Migraron a la formación {formacion} ")

    posicion_coords = obtener_coordenadas_por_formacion(formacion)

    if posicion_coords:
        pitch = Pitch(pitch_type='statsbomb', line_color='black', pitch_color='#aaddaa') 
        fig, ax = pitch.draw(figsize=(10, 7))
        x_coords = [120 - pos[1] for pos in posicion_coords]  
        y_coords = [80 - pos[0] for pos in posicion_coords]  
        pitch.scatter(x_coords, y_coords, ax=ax, c='blue', s=300, edgecolors='black', linewidth=1.5)
        ax.set_title(f"Formación {formacion} en el minuto {minuto} --> Formación invertida {formacion_inver}", fontsize=15)
        st.pyplot(fig)
        
        # ******************* Interno 1 ********************
        
        graficos_resumen = 1
        eventos_validos = eventos_equipo[eventos_equipo['type'].isin(['Pass', 'Carry'])].dropna(subset=['pass_end_location'])
        eventos_validos = eventos_validos[eventos_validos['location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]
        eventos_validos = eventos_validos[eventos_validos['pass_end_location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]

        def calcular_ganancia_metros_hacia_porteria(row):
            loc_inicio = row['location']
            loc_final = row['pass_end_location']
            if isinstance(loc_inicio, list) and isinstance(loc_final, list) and loc_final[0] > loc_inicio[0]:
                return np.sqrt((loc_final[0] - loc_inicio[0]) ** 2 + (loc_final[1] - loc_inicio[1]) ** 2)
            else:
                return 0

        eventos_validos['ganancia_metros_hacia_porteria'] = eventos_validos.apply(calcular_ganancia_metros_hacia_porteria, axis=1)
        eventos_validos = eventos_validos[eventos_validos['ganancia_metros_hacia_porteria'] > 0]

        eventos_validos['location_adjusted'] = eventos_validos['location'].apply(
            lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
        )

        eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
            lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
        )

        st.subheader("Ganancia de metros hacia la portería por parte del contrincante, al momento del cambio táctico.")
        pitch = Pitch(pitch_type='statsbomb', line_color='black')
        fig, ax = pitch.draw(figsize=(10, 7))

        x_coords = eventos_validos['location_adjusted'].apply(lambda x: x[0])
        y_coords = eventos_validos['location_adjusted'].apply(lambda x: x[1])
        ganancia_metros = eventos_validos['ganancia_metros_hacia_porteria']

        bins = [0, 5, 10, 20, 30, 40, 50]
        colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
        cmap = mcolors.ListedColormap(colors)
        norm = mcolors.BoundaryNorm(bins, cmap.N)

        sns.kdeplot(x=x_coords, y=y_coords, weights=ganancia_metros, shade=True, cmap=cmap, ax=ax, alpha=0.6)

        cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
        cbar.set_ticks(bins)
        cbar.set_ticklabels([f'{b} m' for b in bins])
        cbar.set_label('Ganancia de metros hacia la portería por parte del contrincante.' , fontsize=12)
        plt.title('Ganancia de metros hacia la portería por parte del contrincante.', fontsize=14)
        st.write('El gráfico muestra un mapa de calor que ilustra las zonas donde el equipo contrincante logró avanzar hacia la portería. Las áreas más oscuras representan zonas donde hubo mayor cantidad de metros ganados, indicando las áreas más peligrosas para el equipo seleccionado. El gráfico también incluye una barra de colores para mostrar diferentes rangos de metros ganados, estos datos al momento del ajuste táctico.')
        st.pyplot(fig)

        # ******************* Interno 2 ********************

        st.subheader("Zonas de peligro, direcciones del ataque, al momento del cambio táctico.")
        pitch = Pitch(pitch_type='statsbomb', line_color='black')
        fig, ax = pitch.draw(figsize=(10, 7))
        eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
            lambda x: [120 - x[0], x[1]] if x[0] < 60 else x  
        )

        x_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[0])
        y_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[1])
        sns.kdeplot(x=x_coords_end, y=y_coords_end, shade=True, cmap='coolwarm', ax=ax, shade_lowest=False, alpha=0.6)

        for i in range(10, 70, 10):
            ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)
            ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5)

        for i in range(10, 40, 10):
            ax.axhline(40 + i, color='gray', linestyle='--', alpha=0.5)
            ax.axhline(40 - i, color='gray', linestyle='--', alpha=0.5)

        for i in range(10, 70, 10):
            ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
            ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

        for i in range(10, 40, 10):
            ax.axhline(40 + i, color='blue', linestyle='--', alpha=0.5)
            ax.axhline(40 - i, color='blue', linestyle='--', alpha=0.5)

        for i in range(10, 40, 10):
            ax.text(2, 40 + i, f'{i}m', color='blue', fontsize=10)
            ax.text(2, 40 - i, f'{i}m', color='blue', fontsize=10)

        plt.title('Zonas de peligro, direcciones del ataque, al momento del cambio táctico.', fontsize=14)

        st.write('Este gráfico busca representar cómo se distribuyeron los ataques del equipo contrario al momento en que se realizo el cambio táctico del equipo seleccionado. Las zonas con mayor densidad de ataques, marcadas por el mapa de calor, indican las áreas donde el equipo rival pudo generar más peligro. Las líneas y etiquetas de distancia añaden una capa de detalle que permite interpretar mejor la relación entre el ataque y la estructura del campo')

        st.pyplot(fig)
        
        #*************+  Interno 3 ************
        
        st.subheader("Peligrosidad de las zonas conquistadas, al momento del cambio táctico.")
        eventos_equipo = eventos[(eventos['team'] == equipo_seleccionado) & (eventos['period'] == 1)]
        tiros_eventos = eventos_equipo[eventos_equipo['type'] == 'Shot']
        tiros_eventos = tiros_eventos.dropna(subset=['shot_end_location', 'shot_statsbomb_xg'])
        pitch = Pitch(pitch_type='statsbomb', line_color='green')
        fig, ax = pitch.draw(figsize=(10, 7))
        tiros_corner = tiros_eventos[tiros_eventos['play_pattern'] == 'From Corner']
        tiros_juego_abierto = tiros_eventos[tiros_eventos['play_pattern'] != 'From Corner']
        x_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[0])
        y_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[1])
        xg_values_abierto = tiros_juego_abierto['shot_statsbomb_xg']

        x_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[0])
        y_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[1])
        xg_values_corner = tiros_corner['shot_statsbomb_xg']

        scatter_abierto = pitch.scatter(x_shots_abierto, y_shots_abierto, s=xg_values_abierto * 500, 
                                        c=xg_values_abierto, cmap='coolwarm', ax=ax, edgecolors='black', label='Juego Abierto')

        scatter_corner = pitch.scatter(x_shots_corner, y_shots_corner, s=xg_values_corner * 500, 
                                    color='yellow', edgecolors='black', ax=ax, label='Tiros de Esquina')

        for i in range(10, 60, 10):
            ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)  
            ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5) 

        for i in range(10, 40, 10):
            ax.axhline(40 + i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5) 
            ax.axhline(40 - i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5)  

        for i in range(10, 60, 10):
            ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
            ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

        for i in range(10, 40, 10):
            ax.text(5, 40 + i, f'{i}m', color='blue', fontsize=10)
            ax.text(5, 40 - i, f'{i}m', color='blue', fontsize=10)

        plt.colorbar(scatter_abierto)

        ax.legend(loc='upper right')
        plt.title('Expected Goals (xG) por Ubicación de Tiros (Campo Completo - Medición 60 metros)', fontsize=14)
        st.write('Este análisis es útil para identificar las zonas del campo donde se originan los tiros más peligrosos hasta el momento del ajuste táctico, basados en los valores de xG. Específicamente, Las líneas de medición y etiquetas agregan contexto espacial, ayudando a comprender la relación entre las ubicaciones de los tiros y el campo.')
        st.pyplot(fig)
        
        #*************+Interno************

    else:
        st.write(f"No se pudo encontrar una formación predefinida para {formacion}.")

if graficos_resumen == 0:
    st.write("**No hubo cambios en la formacion para este equipo en el primer tiempo.**")

st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽  ")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ")
st.markdown("⚽ ⚽ ⚽ ")
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
#--------------------------------------(FIN) DESGLOSE DEL PRIMER TIEMPO----------------------------------------------

#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< INICIO RECOMENDACION >>>>>>>>> *********************
        
st.header("")
st.header("Considerar realizar ajuste táctico en la siguiente área del terreno de juego (Análisis con el primer tiempo finalizado).", divider=True)
st.write("Tomando como base todo lo ocurrido en el primer tiempo, a continuación encontrarás el resumen en los gráficos donde enfatizamos nuestra atención para entender el comportamiento del primer tiempo y, además, poder hacer el ejercicio de estudiar qué cambios en la formación pudimos haber implementado con base en los datos y la lectura de los gráficos.")

#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(INICIO) -- RECOMENDACION ------------------------------------------------------ 


eventos = sb.events(match_id=partido_id)

# ---------------------------- PRIMER GRÁFICO: GANANCIA DE METROS ----------------------------

st.markdown(
    "<h4 style='color: red;'>Los gráficos muestran cómo el equipo está siendo atacado, no cómo ataca</h4>",
    unsafe_allow_html=True
)

eventos_validos = eventos_equipo[eventos_equipo['type'].isin(['Pass', 'Carry'])].dropna(subset=['pass_end_location'])
eventos_validos = eventos_validos[eventos_validos['location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]
eventos_validos = eventos_validos[eventos_validos['pass_end_location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]

def calcular_ganancia_metros_hacia_porteria(row):
    loc_inicio = row['location']
    loc_final = row['pass_end_location']
    if isinstance(loc_inicio, list) and isinstance(loc_final, list) and loc_final[0] > loc_inicio[0]:
        return np.sqrt((loc_final[0] - loc_inicio[0]) ** 2 + (loc_final[1] - loc_inicio[1]) ** 2)
    else:
        return 0

eventos_validos['ganancia_metros_hacia_porteria'] = eventos_validos.apply(calcular_ganancia_metros_hacia_porteria, axis=1)
eventos_validos = eventos_validos[eventos_validos['ganancia_metros_hacia_porteria'] > 0]
eventos_validos['location_adjusted'] = eventos_validos['location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
)

eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
)

st.subheader("Ganancia de metros hacia la portería por parte del contrincante.")
pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

x_coords = eventos_validos['location_adjusted'].apply(lambda x: x[0])
y_coords = eventos_validos['location_adjusted'].apply(lambda x: x[1])
ganancia_metros = eventos_validos['ganancia_metros_hacia_porteria']

bins = [0, 5, 10, 20, 30, 40, 50]
colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bins, cmap.N)

sns.kdeplot(x=x_coords, y=y_coords, weights=ganancia_metros, shade=True, cmap=cmap, ax=ax, alpha=0.6)

cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{b} m' for b in bins])
cbar.set_label('Ganancia de metros hacia portería (rango) por parte del contrincante.', fontsize=12)

plt.title('Ganancia de metros hacia portería (rango) de parte del contricante', fontsize=14)
st.write('El gráfico muestra un mapa de calor que ilustra las zonas donde el equipo contrincante logró avanzar hacia la portería. Las áreas más oscuras representan zonas donde hubo mayor cantidad de metros ganados, indicando las áreas más peligrosas para el equipo seleccionado. El gráfico también incluye una barra de colores para mostrar diferentes rangos de metros ganados. Esto al finalizar el primer tiempo.')
st.pyplot(fig)

# ---------------------------- SEGUNDO GRÁFICO: MAPA DE CALOR DIRECCIÓN UNIFICADA ----------------------------

st.subheader("Zonas de peligro, direcciones del ataque.")
pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x  
)

x_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[0])
y_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[1])

sns.kdeplot(x=x_coords_end, y=y_coords_end, shade=True, cmap='coolwarm', ax=ax, shade_lowest=False, alpha=0.6)

for i in range(10, 70, 10):
    ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5)

for i in range(10, 40, 10):
    ax.axhline(40 + i, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(40 - i, color='gray', linestyle='--', alpha=0.5)

for i in range(10, 70, 10):
    ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
    ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

for i in range(10, 40, 10):
    ax.axhline(40 + i, color='blue', linestyle='--', alpha=0.5)
    ax.axhline(40 - i, color='blue', linestyle='--', alpha=0.5)

for i in range(10, 40, 10):
    ax.text(2, 40 + i, f'{i}m', color='blue', fontsize=10)
    ax.text(2, 40 - i, f'{i}m', color='blue', fontsize=10)

plt.title('Zonas de peligro, direcciones del ataque', fontsize=14)
st.write('Este gráfico busca representar cómo se distribuyeron los ataques del equipo contrario a lo largo del primer tiempo. Las zonas con mayor densidad de ataques, marcadas por el mapa de calor, indican las áreas donde el equipo rival pudo generar más peligro. Las líneas y etiquetas de distancia añaden una capa de detalle que permite interpretar mejor la relación entre el ataque y la estructura del campo')
st.pyplot(fig)

# ---------------------------- TERCER GRÁFICO: Peligrosidad de las zonas conquistadas ----------------------------
st.subheader("Peligrosidad de las zonas conquistadas")
eventos_equipo = eventos[(eventos['team'] == equipo_seleccionado) & (eventos['period'] == 1)]
tiros_eventos = eventos_equipo[eventos_equipo['type'] == 'Shot']
tiros_eventos = tiros_eventos.dropna(subset=['shot_end_location', 'shot_statsbomb_xg'])
pitch = Pitch(pitch_type='statsbomb', line_color='green')
fig, ax = pitch.draw(figsize=(10, 7))

tiros_corner = tiros_eventos[tiros_eventos['play_pattern'] == 'From Corner']
tiros_juego_abierto = tiros_eventos[tiros_eventos['play_pattern'] != 'From Corner']

x_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[0])
y_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[1])
xg_values_abierto = tiros_juego_abierto['shot_statsbomb_xg']

x_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[0])
y_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[1])
xg_values_corner = tiros_corner['shot_statsbomb_xg']

scatter_abierto = pitch.scatter(x_shots_abierto, y_shots_abierto, s=xg_values_abierto * 500, 
                                c=xg_values_abierto, cmap='coolwarm', ax=ax, edgecolors='black', label='Juego Abierto')

scatter_corner = pitch.scatter(x_shots_corner, y_shots_corner, s=xg_values_corner * 500, 
                               color='yellow', edgecolors='black', ax=ax, label='Tiros de Esquina')

for i in range(10, 60, 10):
    ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)  
    ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5) 

for i in range(10, 40, 10):
    ax.axhline(40 + i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5)  
    ax.axhline(40 - i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5)  

for i in range(10, 60, 10):
    ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
    ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

for i in range(10, 40, 10):
    ax.text(5, 40 + i, f'{i}m', color='blue', fontsize=10)
    ax.text(5, 40 - i, f'{i}m', color='blue', fontsize=10)

plt.colorbar(scatter_abierto)

ax.legend(loc='upper right')
plt.title('Expected Goals (xG) por Ubicación de Tiros (Campo Completo - Medición 60 metros)', fontsize=14)
st.write('Este análisis es útil para identificar las zonas del campo donde se originan los tiros más peligrosos en el primer tiempo, basados en los valores de xG. Específicamente, se puede observar si los cambios tácticos influyeron en la peligrosidad de las áreas de ataque del equipo o de su oponente. Las líneas de medición y etiquetas agregan contexto espacial, ayudando a comprender la relación entre las ubicaciones de los tiros y el campo.')
st.pyplot(fig)

##------------- interno
eventos = sb.events(match_id=match_id)

info_goles = []

goles_recibidos = eventos[(eventos['type'] == 'Shot') & 
                          (eventos['shot_outcome'] == 'Goal') &
                          (eventos['team'] != equipo_seleccionado) &  
                          (eventos['period'] == 1)] 

if goles_recibidos.empty:
    st.write(f"**No se encontraron goles recibidos en contra por {equipo_seleccionado} en el primer tiempo.**")
else:
    if info_goles is None:
        info_goles = []  
        
    pitch = Pitch(pitch_type='statsbomb', line_color='black')
    fig, ax = pitch.draw(figsize=(10, 7))
    colores = sns.color_palette([(0.1, 0.2, 0.5), (0.8, 0.1, 0.3), (0.2, 0.6, 0.3), (0.4, 0.1, 0.6)], len(goles_recibidos))

for i, (index, gol) in enumerate(goles_recibidos.iterrows()):
    color = colores[i]  

    equipo_gol = gol['team']
    minuto_gol = gol['minute']

    info_goles.append({'Equipo': equipo_gol, 'Minuto': minuto_gol, 'Color': color})
    x_gol = gol['shot_end_location'][0]
    y_gol = gol['shot_end_location'][1]
    pitch.scatter(x_gol, y_gol, s=500, c=[color], edgecolors='black', ax=ax, label=f'Gol {i + 1}')

    ax.text(x_gol, y_gol + 2, f'{equipo_gol} ({minuto_gol} min)', color=color, fontsize=12, ha='center')

    secuencia_pases = eventos[(eventos['team'] == gol['team']) & 
                              (eventos['type'] == 'Pass') & 
                              (eventos['minute'] <= minuto_gol)].sort_values(by='minute', ascending=False).head(10)

    for _, pase in secuencia_pases.head(5).iterrows():
        loc_inicio = pase['location']
        loc_fin = pase['pass_end_location']

        if loc_inicio and loc_fin:
            pitch.arrows(loc_inicio[0], loc_inicio[1], 
                         loc_fin[0], loc_fin[1], color=color, ax=ax, width=2, headwidth=5, headlength=5)


if isinstance(info_goles, list) and len(info_goles) == 0:
    st.write("")
elif len(info_goles) > 0:
    st.subheader("Tabla de Goles Recibidos por el equipo selecionado en el Primer Tiempo")
    df_info_goles = pd.DataFrame(info_goles)
    st.dataframe(df_info_goles) 

    ax.set_title(f"Goles recibidos en contra por {equipo_seleccionado} en el primer tiempo y los últimos 5 pases", fontsize=15)
    
    st.pyplot(fig)

st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽  ")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ")
st.markdown("⚽ ⚽ ⚽ ")
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 
#-----------------------------(FIN) -- RECOMENDACION ------------------------------------------------------ 

#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************   
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************
#****************** <<<<<<<<< FIN RECOMENDACION >>>>>>>>> *********************  

st.header("")
st.header("Resumen de la actividad ofensiva del contricante en el segundo tiempo", divider=True)
st.write("Para terminar encontraremos los datos y graficos del resto del encuentro para analizar si funcionaron los ajustes implementados por el DT o si tu deducciones como usuario de esta APP fueron ideales o hubiesen marcado una diferencia.")
st.markdown(
    "<h4 style='color: red;'>Los gráficos muestran cómo fue atacado, no cómo ataco</h4>",
    unsafe_allow_html=True
)

#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----INICIO----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)

eventos_partido = eventos[eventos['period'] == 2]

# ---------------------------- PRIMER GRÁFICO: GANANCIA DE METROS ----------------------------

eventos_validos = eventos_equipo[eventos_equipo['type'].isin(['Pass', 'Carry'])].dropna(subset=['pass_end_location'])

eventos_validos = eventos_validos[eventos_validos['location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]
eventos_validos = eventos_validos[eventos_validos['pass_end_location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]

def calcular_ganancia_metros_hacia_porteria(row):
    loc_inicio = row['location']
    loc_final = row['pass_end_location']
    if isinstance(loc_inicio, list) and isinstance(loc_final, list) and loc_final[0] > loc_inicio[0]:
        return np.sqrt((loc_final[0] - loc_inicio[0]) ** 2 + (loc_final[1] - loc_inicio[1]) ** 2)
    else:
        return 0

eventos_validos['ganancia_metros_hacia_porteria'] = eventos_validos.apply(calcular_ganancia_metros_hacia_porteria, axis=1)
eventos_validos = eventos_validos[eventos_validos['ganancia_metros_hacia_porteria'] > 0]

eventos_validos['location_adjusted'] = eventos_validos['location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
)

eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
)

st.subheader("Ganancia de metros hacia la portería por parte del contricante.")

pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

x_coords = eventos_validos['location_adjusted'].apply(lambda x: x[0])
y_coords = eventos_validos['location_adjusted'].apply(lambda x: x[1])
ganancia_metros = eventos_validos['ganancia_metros_hacia_porteria']

bins = [0, 5, 10, 20, 30, 40, 50]
colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bins, cmap.N)

sns.kdeplot(x=x_coords, y=y_coords, weights=ganancia_metros, shade=True, cmap=cmap, ax=ax, alpha=0.6)

cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{b} m' for b in bins])
cbar.set_label('Ganancia de metros hacia portería (rango)', fontsize=12)
plt.title('Ganancia de metros hacia portería (rango)', fontsize=14)
st.write('El gráfico muestra un mapa de calor que ilustra las zonas donde el equipo contrincante logró avanzar hacia la portería. Las áreas más oscuras representan zonas donde hubo mayor cantidad de metros ganados, indicando las áreas más peligrosas para el equipo seleccionado. El gráfico también incluye una barra de colores para mostrar diferentes rangos de metros ganados durante todo el encuentro.')
st.pyplot(fig)

# ---------------------------- SEGUNDO GRÁFICO: MAPA DE CALOR DIRECCIÓN UNIFICADA ----------------------------

st.subheader("Zonas de peligro, direcciones del ataque.")

pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x  # Invertir X si el pase termina en la mitad izquierda
)

x_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[0])
y_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[1])

sns.kdeplot(x=x_coords_end, y=y_coords_end, shade=True, cmap='coolwarm', ax=ax, shade_lowest=False, alpha=0.6)

for i in range(10, 70, 10):
    ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5)

for i in range(10, 40, 10):
    ax.axhline(40 + i, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(40 - i, color='gray', linestyle='--', alpha=0.5)

for i in range(10, 70, 10):
    ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
    ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

for i in range(10, 40, 10):
    ax.axhline(40 + i, color='blue', linestyle='--', alpha=0.5)
    ax.axhline(40 - i, color='blue', linestyle='--', alpha=0.5)

for i in range(10, 40, 10):
    ax.text(2, 40 + i, f'{i}m', color='blue', fontsize=10)
    ax.text(2, 40 - i, f'{i}m', color='blue', fontsize=10)

plt.title('Zonas de peligro, direccion del ataque', fontsize=14)
st.write('Este gráfico busca representar cómo se distribuyeron los ataques del equipo contrario durante todo el encuentro. Las zonas con mayor densidad de ataques, marcadas por el mapa de calor, indican las áreas donde el equipo rival pudo generar más peligro. Las líneas y etiquetas de distancia añaden una capa de detalle que permite interpretar mejor la relación entre el ataque y la estructura del campo')
st.pyplot(fig)

# ---------------------------- TERCER GRÁFICO: Peligrosidad de las zonas conquistadas ----------------------------
st.subheader("Peligrosidad de las zonas conquistadas")

eventos_equipo = eventos[(eventos['team'] == equipo_seleccionado) & (eventos['period'] == 1)]
tiros_eventos = eventos_equipo[eventos_equipo['type'] == 'Shot']
tiros_eventos = tiros_eventos.dropna(subset=['shot_end_location', 'shot_statsbomb_xg'])

pitch = Pitch(pitch_type='statsbomb', line_color='green')
fig, ax = pitch.draw(figsize=(10, 7))

tiros_corner = tiros_eventos[tiros_eventos['play_pattern'] == 'From Corner']
tiros_juego_abierto = tiros_eventos[tiros_eventos['play_pattern'] != 'From Corner']

x_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[0])
y_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[1])
xg_values_abierto = tiros_juego_abierto['shot_statsbomb_xg']

x_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[0])
y_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[1])
xg_values_corner = tiros_corner['shot_statsbomb_xg']

scatter_abierto = pitch.scatter(x_shots_abierto, y_shots_abierto, s=xg_values_abierto * 500, 
                                c=xg_values_abierto, cmap='coolwarm', ax=ax, edgecolors='black', label='Juego Abierto')

scatter_corner = pitch.scatter(x_shots_corner, y_shots_corner, s=xg_values_corner * 500, 
                               color='yellow', edgecolors='black', ax=ax, label='Tiros de Esquina')

for i in range(10, 60, 10):
    ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5)

for i in range(10, 40, 10):
    ax.axhline(40 + i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5)  # Hacia la derecha
    ax.axhline(40 - i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5)  # Hacia la izquierda

for i in range(10, 60, 10):
    ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
    ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

for i in range(10, 40, 10):
    ax.text(5, 40 + i, f'{i}m', color='blue', fontsize=10)
    ax.text(5, 40 - i, f'{i}m', color='blue', fontsize=10)

plt.colorbar(scatter_abierto)

ax.legend(loc='upper right')
plt.title('Expected Goals (xG) por Ubicación de Tiros (Campo Completo - Medición 60 metros)', fontsize=14)
st.write('Este análisis es útil para identificar las zonas del campo donde se originan los tiros más peligrosos, basados en los valores de xG. Específicamente, se puede observar si los cambios tácticos influyeron en la peligrosidad de las áreas de ataque del equipo o de su oponente. Las líneas de medición y etiquetas agregan contexto espacial, ayudando a comprender la relación entre las ubicaciones de los tiros y el campo.')
st.pyplot(fig)

#-------

info_goles2 = []

goles_recibidos = eventos[(eventos['type'] == 'Shot') & 
                          (eventos['shot_outcome'] == 'Goal') &
                          (eventos['team'] != equipo_seleccionado) & 
                          (eventos['period'] == 2)] 

if goles_recibidos.empty:
    st.write(f"**No se encontraron goles recibidos en contra por {equipo_seleccionado} en el segundo tiempo.**")
else:
    if info_goles2 is None:
        info_goles2 = []  

    pitch = Pitch(pitch_type='statsbomb', line_color='black')
    fig, ax = pitch.draw(figsize=(10, 7))

    colores = sns.color_palette([(0.1, 0.2, 0.5), (0.8, 0.1, 0.3), (0.2, 0.6, 0.3), (0.4, 0.1, 0.6)], len(goles_recibidos))

for i, (index, gol) in enumerate(goles_recibidos.iterrows()):
    color = colores[i] 

    equipo_gol = gol['team']
    minuto_gol = gol['minute']

    info_goles2.append({'Equipo': equipo_gol, 'Minuto': minuto_gol, 'Color': color})

    x_gol = gol['shot_end_location'][0]
    y_gol = gol['shot_end_location'][1]
    pitch.scatter(x_gol, y_gol, s=500, c=[color], edgecolors='black', ax=ax, label=f'Gol {i + 1}')

    ax.text(x_gol, y_gol + 2, f'{equipo_gol} ({minuto_gol} min)', color=color, fontsize=12, ha='center')

    secuencia_pases = eventos[(eventos['team'] == gol['team']) & 
                              (eventos['type'] == 'Pass') & 
                              (eventos['minute'] <= minuto_gol)].sort_values(by='minute', ascending=False).head(10)

    for _, pase in secuencia_pases.head(5).iterrows():
        loc_inicio = pase['location']
        loc_fin = pase['pass_end_location']

        if loc_inicio and loc_fin:
            pitch.arrows(loc_inicio[0], loc_inicio[1], 
                         loc_fin[0], loc_fin[1], color=color, ax=ax, width=2, headwidth=5, headlength=5)


if isinstance(info_goles2, list) and len(info_goles2) == 0:
    st.write("")
elif len(info_goles2) > 0:
    st.subheader("Tabla de Goles Recibidos por el equipo selecionado en el Segundo Tiempo")
    df_info_goles2 = pd.DataFrame(info_goles2)
    st.dataframe(df_info_goles2) 
    
    ax.set_title(f"Goles recibidos en contra por {equipo_seleccionado} en el segundo tiempo y los últimos 5 pases", fontsize=15)

    st.pyplot(fig)
    

def obtener_marcador_final(match_id):
    eventos = sb.events(match_id=match_id)


    goles_local = eventos[(eventos['type'] == 'Shot') & 
                          (eventos['shot_outcome'] == 'Goal') & 
                          (eventos['possession_team'] == eventos['possession_team'].iloc[0])]

    goles_visitante = eventos[(eventos['type'] == 'Shot') & 
                              (eventos['shot_outcome'] == 'Goal') & 
                              (eventos['possession_team'] != eventos['possession_team'].iloc[0])]


    marcador_local_final = len(goles_local)
    marcador_visitante_final = len(goles_visitante)

    teams = eventos['team'].unique()
    home_team = teams[0] 
    away_team = teams[1] 

    st.subheader(f"Marcador final: {home_team} {marcador_local_final} - {marcador_visitante_final} {away_team}")

match_id = partido_id 
marcador_primer = obtener_marcador_final(match_id)

st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽  ")
st.markdown("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ")
st.markdown("⚽ ⚽ ⚽ ")

#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)
#W@@@@@@@@@@@@@@@@@@@@@@@@ ----FIN----->>>>>>>>>>>>>>>>> (RESTO DEL PARTIDO)