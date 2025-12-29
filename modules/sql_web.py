import pyodbc
import streamlit as st
from datetime import datetime

class SQLNexLabConnection:
    
    DEFAULT_SERVER = "LLIMGVENTURA\\SQLEXPRESS"
    DEFAULT_DATABASE = "NexLab_Grau"
    DEFAULT_USERNAME = "sa"
    DEFAULT_PASSWORD = "123"
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self, server, database, username, password):
        try:
            connection_string = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}'
            )
            
            self.connection = pyodbc.connect(connection_string, timeout=10)
            self.cursor = self.connection.cursor()
            return True
            
        except pyodbc.Error as e:
            try:
                connection_string = (
                    f'DRIVER={{SQL Server}};'
                    f'SERVER={server};'
                    f'DATABASE={database};'
                    f'UID={username};'
                    f'PWD={password}'
                )
                self.connection = pyodbc.connect(connection_string, timeout=10)
                self.cursor = self.connection.cursor()
                return True
            except pyodbc.Error as e2:
                st.error(f"Error de conexión: {str(e2)}")
                return False
    
    def connect_default(self):
        return self.connect(
            self.DEFAULT_SERVER,
            self.DEFAULT_DATABASE,
            self.DEFAULT_USERNAME,
            self.DEFAULT_PASSWORD
        )
    
    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"Error al cerrar conexión: {str(e)}")
    
    def search_order(self, numero_orden):
        try:
            if not self.connection or not self.cursor:
                raise Exception("No hay conexión a la base de datos")
            
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
            """
            
            self.cursor.execute(query, (numero_orden,))
            row = self.cursor.fetchone()
            
            if row:
                # Construir nombre completo
                apellidos = f"{row.h_apellido1 or ''} {row.h_apellido2 or ''}".strip()
                nombre_completo = f"{apellidos} {row.h_nombres or ''}".strip()
                
                return {
                    'numero_orden': row.numero_orden,
                    'fecha_creacion': row.fecha_creacion,
                    'estado': row.o_estado,
                    'nombres': row.h_nombres,
                    'apellido2': row.h_apellido2,
                    'nombre_completo': nombre_completo.upper(),
                    'sexo': row.h_sexo
                }
            
            return None
            
        except Exception as e:
            raise Exception(f"Error buscando orden: {str(e)}")
    
    def search_recent_orders(self, limit=50):
        try:
            if not self.connection or not self.cursor:
                raise Exception("No hay conexión a la base de datos")
            
            query = f"""
                SELECT TOP {limit}
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
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            orders = []
            for row in rows:
                # Construir nombre completo
                apellidos = f"{row.h_apellido1 or ''} {row.h_apellido2 or ''}".strip()
                nombre_completo = f"{apellidos} {row.h_nombres or ''}".strip()
                
                orders.append({
                    'numero_orden': row.numero_orden,
                    'fecha_creacion': row.fecha_creacion,
                    'estado': row.o_estado,
                    'nombres': row.h_nombres,
                    'apellido1': row.h_apellido1,
                    'nombre_completo': nombre_completo.upper(),
                    'sexo': row.h_sexo
                })
            
            return orders
            
        except Exception as e:
            raise Exception(f"Error obteniendo órdenes recientes: {str(e)}")
    
    def test_connection(self):
        try:
            if not self.connection:
                return False
            
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
            return True
            
        except Exception:
            return False
