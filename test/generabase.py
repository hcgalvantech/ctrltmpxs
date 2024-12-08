import psycopg2
from psycopg2 import sql
import sys

class DatabaseManager:
    def __init__(self, host='localhost', port=5432, user='evalua', password='Sismas50+'):
        """
        Inicializa la conexión a PostgreSQL.
        
        Args:
            host (str): Dirección del servidor de base de datos
            port (int): Puerto de conexión
            user (str): Usuario de PostgreSQL
            password (str): Contraseña del usuario
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password
        }
        self.connection = None
        self.cursor = None

    def connect(self, database='postgres'):
        """
        Establece una conexión a la base de datos.
        
        Args:
            database (str): Nombre de la base de datos inicial
        """
        try:
            # Usar parámetros de conexión con la base de datos inicial
            self.connection = psycopg2.connect(
                host=self.connection_params['host'],
                port=self.connection_params['port'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                database=database
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            print("Conexión establecida exitosamente.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error al conectar a PostgreSQL: {error}")
            sys.exit(1)

    def crear_base_de_datos(self):
        """
        Crea la base de datos alumnos.
        """
        try:
            # Eliminar la base de datos si existe
            self.cursor.execute("DROP DATABASE IF EXISTS alumnos")
            
            # Crear la base de datos
            self.cursor.execute("CREATE DATABASE alumnos")
            print("Base de datos 'alumnos' creada exitosamente.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error al crear la base de datos: {error}")
            self.connection.rollback()

    def crear_tablas(self):
        """
        Crea las tablas en la base de datos alumnos.
        """
        # Conectar a la base de datos alumnos
        conn_alumnos = psycopg2.connect(
            host=self.connection_params['host'],
            port=self.connection_params['port'],
            user=self.connection_params['user'],
            password=self.connection_params['password'],
            database='alumnos'
        )
        conn_alumnos.autocommit = True
        cursor_alumnos = conn_alumnos.cursor()

        try:
            # Scripts de creación de tablas
            tablas_script = """
            -- Tabla Alumno
            CREATE TABLE alumno (
                id SERIAL PRIMARY KEY,
                dni INTEGER NOT NULL,
                apenom TEXT NOT NULL
            );

            -- Tabla Tecnicatura
            CREATE TABLE tecnicatura (
                id SERIAL PRIMARY KEY,
                tectun TEXT NOT NULL
            );

            -- Tabla Inscriptos
            CREATE TABLE inscriptos (
                id SERIAL PRIMARY KEY,
                iddni INTEGER NOT NULL,
                idtectun INTEGER NOT NULL,
                regular TEXT CHECK (regular IN ('COMPLETO', 'INCOMPLETO')) DEFAULT 'INCOMPLETO',
                FOREIGN KEY (iddni) REFERENCES alumno(id),
                FOREIGN KEY (idtectun) REFERENCES tecnicatura(id)
            );

            -- Tabla Acceso
            CREATE TABLE acceso (
                id SERIAL PRIMARY KEY,
                idins INTEGER NOT NULL,
                acceso BOOLEAN NOT NULL DEFAULT TRUE,
                hora TIMESTAMP,
                link TEXT,
                FOREIGN KEY (idins) REFERENCES inscriptos(id)
            );

            -- Tabla Examen
            CREATE TABLE examen (
                id SERIAL PRIMARY KEY,
                exalink TEXT CHECK (
                    exalink SIMILAR TO 'https://github\\.com/%' OR 
                    exalink SIMILAR TO 'https://[^/]+\\.github\\.com/%' OR 
                    exalink LIKE 'https://gitlab.com/%' OR 
                    exalink LIKE 'https://bitbucket.org/%'
                )
            );

            -- Tabla Turnos
            CREATE TABLE turnos (
                id SERIAL PRIMARY KEY,
                f_desde TIMESTAMP NOT NULL,
                f_hasta TIMESTAMP NOT NULL,
                idtec INTEGER NOT NULL,
                idexa INTEGER NOT NULL,
                FOREIGN KEY (idtec) REFERENCES tecnicatura(id),
                FOREIGN KEY (idexa) REFERENCES examen(id),
                CONSTRAINT check_fecha_valida CHECK (f_desde < f_hasta)
            );

            -- Comentarios explicativos
            COMMENT ON TABLE alumno IS 'Tabla que almacena la información de los alumnos';
            COMMENT ON COLUMN alumno.id IS 'Identificador único generado automáticamente';
            COMMENT ON COLUMN alumno.dni IS 'Documento de identidad del alumno';
            COMMENT ON COLUMN alumno.apenom IS 'Apellido y nombre del alumno';
            """
            
            # Ejecutar script de creación de tablas
            cursor_alumnos.execute(tablas_script)
            print("Tablas creadas exitosamente.")
        
        except (Exception, psycopg2.Error) as error:
            print(f"Error al crear las tablas: {error}")
            conn_alumnos.rollback()
        
        finally:
            cursor_alumnos.close()
            conn_alumnos.close()

    def close_connection(self):
        """
        Cierra la conexión a la base de datos.
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Conexión a PostgreSQL cerrada.")

def main():
    # Configuración de conexión
    # IMPORTANTE: Reemplazar con tus credenciales
    db_manager = DatabaseManager(
        host='localhost',  # Cambiar si es necesario
        port=5432,         # Puerto por defecto de PostgreSQL
        user='evalua',   # Usuario de PostgreSQL
        password='Sismas50+'  # Contraseña de PostgreSQL
    )

    try:
        # Conectar a la base de datos inicial
        db_manager.connect()
        
        # Crear base de datos
        db_manager.crear_base_de_datos()
        
        # Crear tablas
        db_manager.crear_tablas()

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    
    finally:
        # Cerrar conexión
        db_manager.close_connection()

if __name__ == "__main__":
    main()