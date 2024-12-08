import csv
import psycopg2
import os

class DatabaseLoader:
    def __init__(self, host='localhost', port=5432, user='postgres', password='', database='alumnos'):
        """
        Inicializa la conexión a PostgreSQL.
        
        Args:
            host (str): Dirección del servidor de base de datos
            port (int): Puerto de conexión
            user (str): Usuario de PostgreSQL
            password (str): Contraseña del usuario
            database (str): Nombre de la base de datos
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Establece una conexión a la base de datos.
        """
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            print("Conexión establecida exitosamente.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error al conectar a PostgreSQL: {error}")
            raise

    def close_connection(self):
        """
        Cierra la conexión a la base de datos.
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Conexión a PostgreSQL cerrada.")

    def cargar_alumnos(self, archivo_csv):
        """
        Carga datos de alumnos desde un archivo CSV a la tabla alumno.
        
        Args:
            archivo_csv (str): Ruta del archivo CSV con datos de alumnos
        """
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                # Usar punto y coma como separador y permitir comas en nombres
                csv_reader = csv.reader(file, delimiter=';')
                
                # Saltar la primera fila (encabezado)
                next(csv_reader)
                
                # Preparar la consulta de inserción
                consulta = "INSERT INTO alumno (dni, apenom) VALUES (%s, %s)"
                
                # Cargar datos
                for fila in csv_reader:
                    # Validar que la fila tenga 2 columnas
                    if len(fila) == 2:
                        dni, apenom = fila
                        self.cursor.execute(consulta, (dni, apenom))
                
                print(f"Datos de alumnos cargados desde {archivo_csv}")
        
        except FileNotFoundError:
            print(f"Error: Archivo {archivo_csv} no encontrado.")
        except csv.Error as e:
            print(f"Error al leer el archivo CSV: {e}")
        except (Exception, psycopg2.Error) as error:
            print(f"Error al cargar alumnos: {error}")
            self.connection.rollback()
        
    def cargar_tecnicaturas(self, archivo_csv):
        """
        Carga datos de tecnicaturas desde un archivo CSV a la tabla tecnicatura.
        
        Args:
            archivo_csv (str): Ruta del archivo CSV con datos de tecnicaturas
        """
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                # Usar punto y coma como separador
                csv_reader = csv.reader(file, delimiter=';')
                
                # Saltar la primera fila (encabezado)
                next(csv_reader)
                
                # Preparar la consulta de inserción
                consulta = "INSERT INTO tecnicatura (tectun) VALUES (%s)"
                
                # Cargar datos
                for fila in csv_reader:
                    # Validar que la fila tenga 1 columna
                    if len(fila) == 1:
                        tectun = fila[0]
                        self.cursor.execute(consulta, (tectun,))
                
                print(f"Datos de tecnicaturas cargados desde {archivo_csv}")
        
        except FileNotFoundError:
            print(f"Error: Archivo {archivo_csv} no encontrado.")
        except csv.Error as e:
            print(f"Error al leer el archivo CSV: {e}")
        except (Exception, psycopg2.Error) as error:
            print(f"Error al cargar tecnicaturas: {error}")
            self.connection.rollback()

    def cargar_inscriptos(self, archivo_csv):
        """
        Carga datos de inscriptos desde un archivo CSV a la tabla inscriptos.
        Busca los IDs correspondientes de DNI y tecnicatura.
        
        Args:
            archivo_csv (str): Ruta del archivo CSV con datos de inscriptos
        """
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                # Usar punto y coma como separador
                csv_reader = csv.reader(file, delimiter=';')
                
                # Saltar la primera fila (encabezado)
                next(csv_reader)
                
                # Preparar la consulta de búsqueda de IDs
                consulta_id_alumno = "SELECT id FROM alumno WHERE dni = %s"
                consulta_id_tecnicatura = "SELECT id FROM tecnicatura WHERE tectun = %s"
                
                # Preparar la consulta de inserción
                consulta_inscripcion = """
                INSERT INTO inscriptos (iddni, idtectun, regular, email) 
                VALUES (%s, %s, %s, %s)
                """
                
                # Cargar datos
                for fila in csv_reader:
                    # Validar que la fila tenga 4 columnas
                    if len(fila) == 4:
                        dni, tecnicatura, regularidad, email = fila
                        
                        # Buscar ID de alumno
                        self.cursor.execute(consulta_id_alumno, (dni,))
                        id_alumno = self.cursor.fetchone()
                        
                        # Buscar ID de tecnicatura
                        self.cursor.execute(consulta_id_tecnicatura, (tecnicatura,))
                        id_tecnicatura = self.cursor.fetchone()
                        
                        # Validar que se encuentren los IDs
                        if id_alumno and id_tecnicatura:
                            self.cursor.execute(
                                consulta_inscripcion, 
                                (id_alumno[0], id_tecnicatura[0], regularidad, email)
                            )
                        else:
                            print(f"No se encontró ID para DNI {dni} o tecnicatura {tecnicatura}")
                
                print(f"Datos de inscriptos cargados desde {archivo_csv}")
        
        except FileNotFoundError:
            print(f"Error: Archivo {archivo_csv} no encontrado.")
        except csv.Error as e:
            print(f"Error al leer el archivo CSV: {e}")
        except (Exception, psycopg2.Error) as error:
            print(f"Error al cargar inscriptos: {error}")
            self.connection.rollback()
            
def main():
    # Configuración de conexión
    # IMPORTANTE: Reemplazar con tus credenciales
    db_loader = DatabaseLoader(
        host='localhost',      # Cambiar si es necesario
        port=5432,             # Puerto por defecto de PostgreSQL
        user='evalua',       # Usuario de PostgreSQL
        password='Sismas50+',  # Contraseña de PostgreSQL
        database='alumnos'     # Nombre de la base de datos
    )

    try:
        # Conectar a la base de datos
        db_loader.connect()
        
        # 1. Cargar alumnos desde CSV
        db_loader.cargar_alumnos('alumnos.csv')
        
        # 2. Cargar tecnicaturas desde CSV
        db_loader.cargar_tecnicaturas('tecnicaturas.csv')
        
        # 3. Cargar inscriptos desde CSV
        db_loader.cargar_inscriptos('inscriptos.csv')

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    
    finally:
        # Cerrar conexión
        db_loader.close_connection()

if __name__ == "__main__":
    main()