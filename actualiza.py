import pandas as pd
import psycopg2

# Configuración de la conexión a la base de datos
conn = psycopg2.connect(
    dbname="alumnos",
    user="evalua",
    password="Sismas88+",
    host="69.46.1.49"
)

# Crear un cursor
cursor = conn.cursor()

# Leer el archivo XLSX
df = pd.read_excel('datos.xlsx')

# Preparar la consulta de inserción
insert_query = """
INSERT INTO turnos (f_desde, f_hasta, idtec, idexa, regular, tiempo)
VALUES (%s, %s, %s, %s, %s, %s)
"""

# Iterar sobre las filas del DataFrame e insertar en la base de datos
for index, row in df.iterrows():
    # Mapear las columnas del DataFrame a los campos de la tabla
    valores = (
        row['f_desde'],  # Asegúrate de que el nombre de la columna coincida con tu Excel
        row['f_hasta'], 
        row['idtec'], 
        row['idexa'], 
        row['regular'], 
        row['tiempo']
    )
    
    try:
        cursor.execute(insert_query, valores)
    except Exception as e:
        print(f"Error al insertar fila {index}: {e}")
        conn.rollback()
    else:
        conn.commit()

# Cerrar cursor y conexión
cursor.close()
conn.close()

print("Inserción de datos completada.")