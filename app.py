import streamlit as st
from statsbombpy import sb
from fpdf import FPDF
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd

# Añadir un título en la barra lateral
st.sidebar.markdown("<h1 style='text-align: center; color: black;'>Sheplays Analytics</h1>", unsafe_allow_html=True)

# Descripción en la barra lateral
st.sidebar.write("""
    El equipo que eligas sera analizado en el 1er tiempo para entender como esta siendo atacado ofensivamente, esto con la finalidad de identificar cambios tacticos en el equipo para el 2do tiempo.
""")

# Título en el main content area
st.title("Herramienta de análisis sobre la peligrosidad de las zonas conquistadas VS el parado táctico")

# Torneo fijo (Euro 2024)
torneo_seleccionado = "Euro 2024"
st.sidebar.subheader(f"Torneo: {torneo_seleccionado}")

# Obtener los partidos del torneo seleccionado
torneo_id = 55  # Euro 2024 tiene el competition_id=55
partidos_torneo = sb.matches(competition_id=torneo_id, season_id=282)

# Crear un diccionario de los partidos con sus nombres y el tipo de encuentro (competition_stage)
partidos_dict = {}
for index, row in partidos_torneo.iterrows():
    stage_name = row['competition_stage']['name'] if row['competition_stage'] and 'name' in row['competition_stage'] else 'Desconocido'
    partido_nombre = f"{row['home_team']} vs {row['away_team']} ({stage_name})"
    partidos_dict[partido_nombre] = row['match_id']

# Seleccionar partido

#partido_seleccionado = st.selectbox("Selecciona el encuentro:", list(partidos_dict.keys()))
partido_seleccionado = st.sidebar.selectbox("Selecciona el encuentro:", list(partidos_dict.keys()))

# Obtener el ID del partido seleccionado
partido_id = partidos_dict[partido_seleccionado]

st.sidebar.write(f"Has seleccionado el encuentro: **{partido_seleccionado}** con Match ID: **{partido_id}**")


# Obtener los eventos del partido seleccionado
eventos = sb.events(match_id=partido_id)


# Obtener los nombres de los equipos
equipo_local = eventos['team'].iloc[0]['name'] if isinstance(eventos['team'].iloc[0], dict) else eventos['team'].iloc[0]
equipo_visitante = eventos['team'].iloc[1]['name'] if isinstance(eventos['team'].iloc[1], dict) else eventos['team'].iloc[1]


# Seleccionar el equipo para analizar en la barra lateral
equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo a analizar:", [equipo_local, equipo_visitante])

st.sidebar.write(f"Has seleccionado analizar al equipo: **{equipo_seleccionado}**")

# Filtrar eventos solo del equipo seleccionado
eventos_equipo = eventos[eventos['team'] == equipo_seleccionado]

#-----------------------------RESUMEN 1 ------------------------------------------------------


# Función para cargar eventos con caché para optimizar el rendimiento
@st.cache_data
def cargar_eventos(partido_id):
    return sb.events(match_id=partido_id)

# Cargar los eventos del partido seleccionado
eventos = cargar_eventos(partido_id)

# Filtrar los eventos del primer tiempo (primeros 45 minutos)
eventos_partido = eventos[eventos['period'] == 1]

# Obtener los equipos que jugaron ese partido
equipos = eventos_partido['team'].unique()

# Verificar que hay datos suficientes
if len(equipos) >= 2:
    # Obtener la lista de jugadores por equipo
    jugadores_equipo1 = eventos_partido[eventos_partido['team'] == equipos[0]]['player'].unique()
    jugadores_equipo2 = eventos_partido[eventos_partido['team'] == equipos[1]]['player'].unique()

    # Filtrar las sustituciones (eventos de tipo 'Substitution') que ocurrieron en el primer tiempo
    cambios_equipo1 = eventos_partido[(eventos_partido['team'] == equipos[0]) & (eventos_partido['type'] == 'Substitution')]
    cambios_equipo2 = eventos_partido[(eventos_partido['team'] == equipos[1]) & (eventos_partido['type'] == 'Substitution')]

    # Mostrar la información del partido en la app
    st.header("Resumen 1er tiempo")
    st.write(f"**Equipos:** {equipos[0]} vs {equipos[1]}")

    # Mostrar los jugadores del primer equipo
    st.subheader(f"Jugadores del {equipos[0]} en el primer tiempo:")
    for jugador in jugadores_equipo1:
        st.write(f"- {jugador}")

    # Mostrar los cambios del primer equipo (si los hubo)
    if not cambios_equipo1.empty:
        st.subheader(f"Cambios en el {equipos[0]} en el primer tiempo:")
        for index, row in cambios_equipo1.iterrows():
            st.write(f"- {row['player']} fue sustituido por {row['substitution_replacement']} al minuto {row['minute']}")
    else:
        st.write(f"No hubo cambios en el {equipos[0]} en el primer tiempo.")

    # Mostrar los jugadores del segundo equipo
    st.subheader(f"Jugadores del {equipos[1]} en el primer tiempo:")
    for jugador in jugadores_equipo2:
        st.write(f"- {jugador}")

    # Mostrar los cambios del segundo equipo (si los hubo)
    if not cambios_equipo2.empty:
        st.subheader(f"Cambios en el {equipos[1]} en el primer tiempo:")
        for index, row in cambios_equipo2.iterrows():
            st.write(f"- {row['player']} fue sustituido por {row['substitution_replacement']} al minuto {row['minute']}")
    else:
        st.write(f"No hubo cambios en el {equipos[1]} en el primer tiempo.")
else:
    st.write("No hay datos suficientes para mostrar información sobre este partido.")

# ---------------------------- PRIMER GRÁFICO: GANANCIA DE METROS ----------------------------

# Filtrar eventos de tipo 'Pass' o 'Carry' que tienen ubicación final
eventos_validos = eventos_equipo[eventos_equipo['type'].isin(['Pass', 'Carry'])].dropna(subset=['pass_end_location'])

# Verificar que las columnas 'location' y 'pass_end_location' contengan listas de dos elementos
eventos_validos = eventos_validos[eventos_validos['location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]
eventos_validos = eventos_validos[eventos_validos['pass_end_location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]

# Calcular la distancia recorrida por el equipo tras el pase o carry, pero solo si es hacia la portería rival
def calcular_ganancia_metros_hacia_porteria(row):
    loc_inicio = row['location']
    loc_final = row['pass_end_location']
    if isinstance(loc_inicio, list) and isinstance(loc_final, list) and loc_final[0] > loc_inicio[0]:
        return np.sqrt((loc_final[0] - loc_inicio[0]) ** 2 + (loc_final[1] - loc_inicio[1]) ** 2)
    else:
        return 0

# Aplicar la función para calcular la ganancia de terreno
eventos_validos['ganancia_metros_hacia_porteria'] = eventos_validos.apply(calcular_ganancia_metros_hacia_porteria, axis=1)

# Filtrar eventos que realmente ganaron metros hacia la portería
eventos_validos = eventos_validos[eventos_validos['ganancia_metros_hacia_porteria'] > 0]

# Ajustar las coordenadas para unificar la dirección de ataque (hacia la derecha)
eventos_validos['location_adjusted'] = eventos_validos['location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
)

eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x
)

# Crear el gráfico del campo de fútbol
st.subheader("Mapa de Calor de Ganancia de Metros hacia la Portería")

# Crear el campo de fútbol
pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

# Extraer las ubicaciones ajustadas y la ganancia de metros hacia la portería
x_coords = eventos_validos['location_adjusted'].apply(lambda x: x[0])
y_coords = eventos_validos['location_adjusted'].apply(lambda x: x[1])
ganancia_metros = eventos_validos['ganancia_metros_hacia_porteria']

# Definir los límites de la ganancia de metros y los colores discretos
bins = [0, 5, 10, 20, 30, 40, 50]
colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bins, cmap.N)

# Crear el mapa de calor basado en la ganancia de metros
sns.kdeplot(x=x_coords, y=y_coords, weights=ganancia_metros, shade=True, cmap=cmap, ax=ax, alpha=0.6)

# Crear la barra de color personalizada
cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{b} m' for b in bins])
cbar.set_label('Ganancia de metros hacia portería (rango)', fontsize=12)

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

# ---------------------------- SEGUNDO GRÁFICO: MAPA DE CALOR DIRECCIÓN UNIFICADA ----------------------------

st.subheader("Mapa de Calor con Dirección de Ataque Unificada")

# Crear el campo de fútbol
pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

# Ajustar las coordenadas X para unificar la dirección de ataque hacia la derecha
eventos_validos['pass_end_location_adjusted'] = eventos_validos['pass_end_location'].apply(
    lambda x: [120 - x[0], x[1]] if x[0] < 60 else x  # Invertir X si el pase termina en la mitad izquierda
)

# Extraer las posiciones finales de los pases/tiros ajustadas
x_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[0])
y_coords_end = eventos_validos['pass_end_location_adjusted'].apply(lambda x: x[1])

# Crear el mapa de calor de las ubicaciones de los eventos hacia la misma dirección de ataque (derecha)
sns.kdeplot(x=x_coords_end, y=y_coords_end, shade=True, cmap='coolwarm', ax=ax, shade_lowest=False, alpha=0.6)

# Añadir líneas cada 10 metros a partir del centro del campo
for i in range(10, 70, 10):
    ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5)

# Añadir líneas horizontales cada 10 metros
for i in range(10, 40, 10):
    ax.axhline(40 + i, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(40 - i, color='gray', linestyle='--', alpha=0.5)

# Añadir etiquetas de distancia desde el centro del campo
for i in range(10, 70, 10):
    ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
    ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

# Líneas horizontales desde el centro de las porterías hacia las esquinas
for i in range(10, 40, 10):
    ax.axhline(40 + i, color='blue', linestyle='--', alpha=0.5)
    ax.axhline(40 - i, color='blue', linestyle='--', alpha=0.5)

# Añadir etiquetas de distancia desde la portería hacia las bandas
for i in range(10, 40, 10):
    ax.text(2, 40 + i, f'{i}m', color='blue', fontsize=10)
    ax.text(2, 40 - i, f'{i}m', color='blue', fontsize=10)

# Título del gráfico
plt.title('Mapa de Calor con Dirección de Ataque Unificada (Ataque hacia la derecha)', fontsize=14)

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

# ---------------------------- TERCER GRÁFICO: Peligrosidad de las zonas conquistadas ----------------------------
st.subheader("Peligrosidad de las zonas conquistadas")

# Filtrar eventos del equipo seleccionado y del primer tiempo
eventos_equipo = eventos[(eventos['team'] == equipo_seleccionado) & (eventos['period'] == 1)]

# Filtrar eventos de tipo 'Shot' y que tengan valores de xG
tiros_eventos = eventos_equipo[eventos_equipo['type'] == 'Shot']
tiros_eventos = tiros_eventos.dropna(subset=['shot_end_location', 'shot_statsbomb_xg'])

# Crear el campo de fútbol completo (sin 'half=True' para mostrar el campo completo)
pitch = Pitch(pitch_type='statsbomb', line_color='green')
fig, ax = pitch.draw(figsize=(10, 7))

# Filtrar tiros provenientes de un tiro de esquina ('From Corner')
tiros_corner = tiros_eventos[tiros_eventos['play_pattern'] == 'From Corner']

# Filtrar tiros en juego abierto ('Open Play') o cualquier otro patrón
tiros_juego_abierto = tiros_eventos[tiros_eventos['play_pattern'] != 'From Corner']

# Extraer las ubicaciones y los valores de xG para tiros de juego abierto
x_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[0])
y_shots_abierto = tiros_juego_abierto['shot_end_location'].apply(lambda x: x[1])
xg_values_abierto = tiros_juego_abierto['shot_statsbomb_xg']

# Extraer las ubicaciones y los valores de xG para tiros de esquina
x_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[0])
y_shots_corner = tiros_corner['shot_end_location'].apply(lambda x: x[1])
xg_values_corner = tiros_corner['shot_statsbomb_xg']

# Dibujar los tiros de juego abierto (color basado en xG)
scatter_abierto = pitch.scatter(x_shots_abierto, y_shots_abierto, s=xg_values_abierto * 500, 
                                c=xg_values_abierto, cmap='coolwarm', ax=ax, edgecolors='black', label='Juego Abierto')

# Dibujar los tiros de esquina (color amarillo)
scatter_corner = pitch.scatter(x_shots_corner, y_shots_corner, s=xg_values_corner * 500, 
                               color='yellow', edgecolors='black', ax=ax, label='Tiros de Esquina')

# Añadir líneas de medición (solo 60 metros a partir del centro del campo hacia las porterías)
for i in range(10, 60, 10):
    ax.axvline(60 + i, color='gray', linestyle='--', alpha=0.5)  # Desde el centro hacia la derecha
    ax.axvline(60 - i, color='gray', linestyle='--', alpha=0.5)  # Desde el centro hacia la izquierda

# Añadir líneas laterales horizontales desde el centro de la portería hacia las esquinas del campo visible
for i in range(10, 40, 10):
    ax.axhline(40 + i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5)  # Hacia la derecha
    ax.axhline(40 - i, xmin=0.05, xmax=0.95, color='blue', linestyle='--', alpha=0.5)  # Hacia la izquierda

# Etiquetas de distancia desde el centro del campo (verticales)
for i in range(10, 60, 10):
    ax.text(60 + i + 1, 42, f'{i}m', color='black', fontsize=10)
    ax.text(60 - i - 5, 42, f'{i}m', color='black', fontsize=10)

# Etiquetas de distancia desde la portería hacia las bandas (horizontales)
for i in range(10, 40, 10):
    ax.text(5, 40 + i, f'{i}m', color='blue', fontsize=10)
    ax.text(5, 40 - i, f'{i}m', color='blue', fontsize=10)

# Añadir barra de color para los tiros de juego abierto (xG)
plt.colorbar(scatter_abierto)

# Añadir título y leyenda
ax.legend(loc='upper right')
plt.title('Expected Goals (xG) por Ubicación de Tiros (Campo Completo - Medición 60 metros)', fontsize=14)

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

st.header("Desglose 1er tiempo")

#--------------------------------------DESGLOSE DEL PRIMER TIEMPO----------------------------------------------
# Definir coordenadas fijas para las posiciones en formaciones comunes (ejemplo 4-3-3, 4-4-2, etc.)
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
    343: [(40, 80),                       # Delantero
          (30, 70), (50, 70),             # Mediocampistas ofensivos
          (40, 55),                       # Mediocentro defensivo
          (20, 65), (60, 65),             # Laterales
          (10, 40), (30, 40), (50, 40),   # Defensas
          (40, 20)],                      # Portero
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

# Obtener los eventos de un partido específico
eventos = sb.events(match_id=partido_id)

# Filtrar los eventos tácticos (parados tácticos)
cambios_tacticos = eventos[eventos['type'] == 'Tactical Shift']

# Revisar los eventos tácticos para ver cómo cambió la formación
for index, row in cambios_tacticos.iterrows():
    minuto = row['minute']  # Minuto del cambio táctico
    formacion = row['tactics']['formation']  # Formación táctica en ese momento
    alineacion = row['tactics']['lineup']  # Alineación de jugadores en esa formación

    st.write(f"Minuto {minuto}: Migraron a la formación {formacion}")

    # Obtener coordenadas basadas en la formación
    posicion_coords = obtener_coordenadas_por_formacion(formacion)

    if posicion_coords:
        # Crear el campo de fútbol usando mplsoccer
        pitch = Pitch(pitch_type='statsbomb', line_color='black', pitch_color='#aaddaa')  # Campo verde claro
        fig, ax = pitch.draw(figsize=(10, 7))

        # Intercambiar las coordenadas para que la orientación sea horizontal
        x_coords = [pos[1] for pos in posicion_coords]  # Usar y como x
        y_coords = [pos[0] for pos in posicion_coords]  # Usar x como y
        
        # Dibujar los jugadores en el campo basados en las posiciones predefinidas
        pitch.scatter(x_coords, y_coords, ax=ax, c='blue', s=300, edgecolors='black', linewidth=1.5)
        
        # Añadir el título del gráfico con el minuto del cambio táctico
        ax.set_title(f"Formación {formacion} en el minuto {minuto}", fontsize=15)

        # Mostrar el gráfico en la app de Streamlit
        st.pyplot(fig)
    else:
        st.write(f"No se pudo encontrar una formación predefinida para {formacion}.")