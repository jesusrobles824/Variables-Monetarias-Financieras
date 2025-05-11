import requests
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
from datetime import datetime
import re
import datetime

url = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias"
params = {"limit": "1"}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    results = data['results']
    Variables = pd.DataFrame(results)[['idVariable', 'descripcion']]
    Variables.set_index('idVariable', inplace=True)
    Variables.to_excel('variables.xlsx', index=True)
else:
    print(f"Error {response.status_code}: {response.text}")
    
lista = [77,78,79,80,81,82]
lista_variables = {}
hoy = datetime.date.today()
hoy = hoy.strftime('%Y-%m-%d')

for id in lista:
 url = f"https://api.bcra.gob.ar/estadisticas/v3.0/monetarias/{id}"
 params = {"desde": "2023-12-10",
           "hasta": hoy}
 response = requests.get(url, params=params)
 if response.status_code == 200:
     data = response.json()
     results = data['results']
     Variable = pd.DataFrame(results)[['fecha', 'valor']]
     Variable.set_index('fecha', inplace=True)
     nombre = Variables.loc[id, "descripcion"]
     Variable.columns = [nombre]
     Variable = Variable[::-1]
     lista_variables[id] = Variable
 else:
     print(f"Error {response.status_code} : {response.text}")
     
Variacion_Reservas = pd.concat(lista_variables.values(), axis=1)
Variacion_Reservas.index = pd.to_datetime(Variacion_Reservas.index)

Variacion_Acumulada = Variacion_Reservas.cumsum()
Variacion_Acumulada.columns = ['Variación acumulada', 'Compra/Venta MULC', 'Operaciones con organismos internacionales', 'Otras operaciones del sector público', 'Variación por efectivo mínimo', 'Otras operaciones no incluidas en otros rubros']
Variacion_Acumulada.index = pd.to_datetime(Variacion_Acumulada.index)
print(Variacion_Acumulada)
ultimo = Variacion_Acumulada.index[-1].date()
mes = ultimo.month
print(mes)
fin_mes = (ultimo + pd.offsets.MonthEnd(0)).date()
ultimo = ultimo.strftime('%d-%m-%Y')

# Establecer el estilo
sns.set(style='white')
plt.figure(figsize=(14,8))
# Usar paleta de colores automática de seaborn
colors = ["#1b5e8c", "#3aaa35", "#e07b39", "#b32d6d", "#6c5e9c", "#2d7f5e"]
#colors = sns.color_palette("husl")
# Crear una lista de patches
patches = []
# Graficar cada columna de Variacion_Acumulada con su respectivo color
for i, columna in enumerate(Variacion_Acumulada.columns):
    # Graficar cada línea
    plt.plot(Variacion_Acumulada.index, Variacion_Acumulada[columna], 
             linewidth=3, label=columna, color=colors[i])
    # Crear un patch para la leyenda con el color de la línea
    patches.append(mpatches.Patch(color=colors[i], label=columna))
    # Obtener el último valor y la última fecha
    last_value = Variacion_Acumulada[columna].iloc[-1]
    last_date = Variacion_Acumulada.index[-1]
    # Mover el último valor 10 días a la derecha (ajustar la fecha)
    adjusted_date = last_date + pd.Timedelta(days=2)
    # Graficar el valor ajustado en el gráfico (con 1 decimal) solo si no es uno de los casos anteriores
    plt.text(adjusted_date, last_value, f'{last_value:.1f}', 
             color=colors[i], fontsize=13, ha='left', va='bottom', weight='bold')
plt.suptitle('Reservas Internacionales', fontsize=26, color='#003366', weight='bold', x=0.2, y=0.95)
plt.title('Variación acumulada por rubro - En millones de dólares', fontsize=14, color='black', alpha=0.55, weight='bold', pad=65, x=0.192)
plt.gca().set_xticks([])
plt.xlabel(f'Fuente: Jesús Robles en base a BCRA. Observaciones con frecuencia diaria al {ultimo}.', labelpad=20, fontsize=11.5, x=0.26)
plt.xlim(pd.Timestamp('2023-12-01'), fin_mes)
for year in range(2023,2026):
 plt.vlines(pd.Timestamp(f'{year}-12-31'), -12000,30000, color='gray', linestyle='-', linewidth=0.7)
 if year == 2023:
     plt.text(pd.Timestamp('2023-12-15'), 28980, 2023, alpha=0.9, ha='center', va='center_baseline', fontsize=12)
 if year == 2024:
     plt.text(pd.Timestamp('2024-06-30'), 28980, 2024, alpha=0.9, ha='center', va='center_baseline', fontsize=12)
 if year == 2025:
     plt.text(pd.Timestamp('2025-03-17'), 28980, 2025, alpha=0.9, ha='center', va='center_baseline', fontsize=12)
 meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
 for month, letra in enumerate(meses, start=1): 
       # Obtener el primer día del mes
       fecha = pd.Timestamp(year, month, 15) 
       if year == 2023 and month < 12:
        continue 
       if year == 2025 and month>mes:
        break
       plt.text(fecha, 26950, letra, color='black', alpha=0.9, ha='center', va='center_baseline', fontsize=10)
       last_day = pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd(0)  # Último día del mes
       if not (year == 2025 and month == mes):
         plt.vlines(last_day, -12000, 28000, color='gray', linestyle='-', linewidth=0.5) 
y_values = list(range(-12000,26001,2000))
for y in y_values:
    plt.gca().hlines(y, pd.Timestamp('2023-12-01'), fin_mes, color='gray', linestyle='--', linewidth=0.5)
plt.yticks(y_values)  
plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
plt.gca().tick_params(axis='y', labelsize='13')
plt.gca().hlines(28000, pd.Timestamp('2023-12-01'), fin_mes, color='gray', linestyle='-', linewidth=0.6)
plt.gca().hlines(30000, pd.Timestamp('2023-12-01'), fin_mes, color='gray', linestyle='-', linewidth=0.6)
plt.ylim(-12000, 30000)
# Agregar la leyenda usando los patches
plt.legend(handles=patches, loc="upper center", frameon=False, handlelength=0.8, handleheight=0.8, ncol=3, bbox_to_anchor=(0.49,1.13), columnspacing=2, fontsize=12)
plt.text(0.9, 1.16, '@JesusRobles824', fontsize=13, color='black', weight='bold', transform=plt.gca().transAxes, ha='right')
# Ajustar el diseño y mostrar el gráfico
plt.tight_layout()
sns.despine(left=True, bottom=False)
plt.gca().spines['bottom'].set_color('gray')
plt.show()
