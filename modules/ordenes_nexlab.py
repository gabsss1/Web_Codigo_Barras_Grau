"""
Módulo para buscar órdenes en la base de datos SQL Server (Nexlab)
Genera etiquetas con información de pacientes
"""
import pyodbc
from datetime import datetime

class OrdenesNexlab:
    """Clase para manejar conexión con base de datos de órdenes Nexlab"""
    
    def __init__(self):
        # Configuración de conexión a SQL Server (AJUSTAR ESTAS CREDENCIALES)
        self.server = ''  # Ejemplo: 'localhost' o '192.168.1.100'
        self.database = ''  # Ejemplo: 'NexlabDB'
        self.username = ''  # Ejemplo: 'sa' o 'nexlab_user'
        self.password = ''  # Ejemplo: 'MiContraseña123'
        self.connection = None
        
    def get_available_driver(self):
        """
        Detecta el driver ODBC disponible en el sistema
        
        Returns:
            str: Nombre del driver disponible o None
        """
        drivers = pyodbc.drivers()
        
        # Orden de preferencia de drivers
        preferred_drivers = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 13 for SQL Server',
            'ODBC Driver 11 for SQL Server',
            'SQL Server Native Client 11.0',
            'SQL Server Native Client 10.0',
            'SQL Server'
        ]
        
        for driver in preferred_drivers:
            if driver in drivers:
                return driver
        
        # Si no encuentra ninguno de los preferidos, retorna el primero que contenga "SQL Server"
        for driver in drivers:
            if 'SQL Server' in driver:
                return driver
        
        return None
    
    def conectar(self):
        """
        Establece conexión con la base de datos SQL Server
        
        Returns:
            tuple: (bool, str) - (éxito, mensaje de error si hay)
        """
        try:
            # Detectar driver disponible
            driver = self.get_available_driver()
            
            if not driver:
                available_drivers = pyodbc.drivers()
                return False, (
                    f"No se encontró ningún driver ODBC para SQL Server instalado.\n"
                    f"Drivers disponibles: {', '.join(available_drivers) if available_drivers else 'Ninguno'}\n\n"
                    f"Por favor instala un driver ODBC desde:\n"
                    f"https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server"
                )
            
            # String de conexión para SQL Server
            connection_string = (
                f'DRIVER={{{driver}}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password}'
            )
            
            self.connection = pyodbc.connect(connection_string)
            return True, None
            
        except pyodbc.Error as e:
            error_msg = str(e)
            driver_info = self.get_available_driver()
            return False, (
                f"Error de conexión: {error_msg}\n\n"
                f"Driver detectado: {driver_info or 'Ninguno'}\n"
                f"Servidor: {self.server}\n"
                f"Base de datos: {self.database}\n"
                f"Usuario: {self.username}"
            )
    
    def desconectar(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except:
                pass
    
    def listar_drivers_disponibles(self):
        """
        Lista todos los drivers ODBC disponibles en el sistema
        
        Returns:
            list: Lista de drivers disponibles
        """
        try:
            return pyodbc.drivers()
        except:
            return []
    
    def buscar_orden(self, numero_orden):
        """
        Busca una orden específica en la base de datos
        
        Args:
            numero_orden (str): Número de orden a buscar (ej: '1622485')
            
        Returns:
            tuple: (bool, dict/str) - (éxito, datos de orden o mensaje de error)
        """
        try:
            if not self.connection:
                conectado, error = self.conectar()
                if not conectado:
                    return False, f"Error de conexión: {error}"
            
            cursor = self.connection.cursor()
            
            # Query para buscar la orden específica
            query = """
                SELECT
                    o.o_numero              AS numero_orden,
                    o.o_fecha               AS fecha_creacion,
                    o.o_estado,
                    h.h_nombres,
                    h.h_apellido1,
                    h.h_apellido2,
                    h.h_sexo
                FROM Ordenes o
                INNER JOIN Historias h
                    ON o.o_his_id = h.h_id
                WHERE o.o_numero = ?
                ORDER BY o.o_fecha DESC
            """
            
            cursor.execute(query, (numero_orden,))
            row = cursor.fetchone()
            
            if row:
                # Convertir resultado a diccionario
                orden_data = {
                    'numero_orden': row.numero_orden,
                    'fecha_creacion': row.fecha_creacion,
                    'estado': row.o_estado,
                    'nombres': row.h_nombres or '',
                    'apellido1': row.h_apellido1 or '',
                    'apellido2': row.h_apellido2 or '',
                    'sexo': row.h_sexo or ''
                }
                cursor.close()
                return True, orden_data
            else:
                cursor.close()
                return False, f"No se encontró la orden {numero_orden}"
                
        except pyodbc.Error as e:
            return False, f"Error en la consulta: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def generar_etiqueta_texto(self, orden_data):
        """
        Genera el texto formateado para la etiqueta
        
        Args:
            orden_data (dict): Datos de la orden
            
        Returns:
            dict: Diccionario con datos formateados para etiqueta
        """
        # Formatear número de orden (agregar .01)
        numero_etiqueta = f"{orden_data['numero_orden']}.01"
        
        # Formatear nombre completo (Apellido1 Apellido2, Nombres)
        apellidos = f"{orden_data['apellido1']} {orden_data['apellido2']}".strip()
        nombres = orden_data['nombres'].strip()
        nombre_completo = f"{apellidos}, {nombres}" if apellidos and nombres else (apellidos or nombres)
        
        # Formatear sexo
        sexo = orden_data['sexo'].upper()
        if sexo == 'M' or sexo.startswith('MASC'):
            sexo_texto = 'MASCULINO'
        elif sexo == 'F' or sexo.startswith('FEM'):
            sexo_texto = 'FEMENINO'
        else:
            sexo_texto = sexo
        
        # Fecha actual
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        return {
            'codigo': numero_etiqueta,
            'nombre': nombre_completo,
            'sexo': sexo_texto,
            'fecha': fecha_actual,
            'orden_original': orden_data['numero_orden']
        }
    
    def listar_ordenes_recientes(self, limite=50):
        """
        Lista las órdenes más recientes
        
        Args:
            limite (int): Número máximo de órdenes a retornar
            
        Returns:
            tuple: (bool, list/str) - (éxito, lista de órdenes o mensaje de error)
        """
        try:
            if not self.connection:
                conectado, error = self.conectar()
                if not conectado:
                    return False, f"Error de conexión: {error}"
            
            cursor = self.connection.cursor()
            
            query = """
                SELECT TOP (?)
                    o.o_numero              AS numero_orden,
                    o.o_fecha               AS fecha_creacion,
                    o.o_estado,
                    h.h_nombres,
                    h.h_apellido1,
                    h.h_apellido2,
                    h.h_sexo
                FROM Ordenes o
                INNER JOIN Historias h
                    ON o.o_his_id = h.h_id
                ORDER BY o.o_fecha DESC
            """
            
            cursor.execute(query, (limite,))
            rows = cursor.fetchall()
            
            ordenes = []
            for row in rows:
                ordenes.append({
                    'numero_orden': row.numero_orden,
                    'fecha_creacion': row.fecha_creacion,
                    'estado': row.o_estado,
                    'nombres': row.h_nombres or '',
                    'apellido1': row.h_apellido1 or '',
                    'apellido2': row.h_apellido2 or '',
                    'sexo': row.h_sexo or ''
                })
            
            cursor.close()
            return True, ordenes
            
        except pyodbc.Error as e:
            return False, f"Error en la consulta: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def test_conexion(self):
        """
        Prueba la conexión a la base de datos
        
        Returns:
            tuple: (bool, str) - (éxito, mensaje)
        """
        try:
            conectado, error = self.conectar()
            if conectado:
                self.desconectar()
                return True, "Conexión exitosa a la base de datos"
            else:
                return False, error
        except Exception as e:
            return False, f"Error probando conexión: {str(e)}"
