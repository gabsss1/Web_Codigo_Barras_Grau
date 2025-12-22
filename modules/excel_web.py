"""
Módulo para leer archivos Excel en la versión web
Adaptación del lector original para Streamlit
"""
import pandas as pd
import os
from typing import List, Dict, Optional

class ExcelWebReader:
    """Clase para leer y procesar archivos Excel en la versión web"""
    
    def __init__(self):
        self.data = None
        self.file_path = None
        self.df = None
        self.header_row = 0
        
    def load_excel_with_header(self, file_path: str, header_row: int = 0, sheet_name: str = None) -> bool:
        """
        Carga un archivo Excel con fila de encabezado personalizada
        
        Args:
            file_path (str): Ruta al archivo Excel
            header_row (int): Número de fila donde están los encabezados (0-based)
            sheet_name (str, optional): Nombre de la hoja
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
            
            self.header_row = header_row
            
            # Leer Excel con header personalizado
            if sheet_name:
                self.df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            else:
                self.df = pd.read_excel(file_path, header=header_row)
            
            # Limpiar datos
            self.df = self.df.dropna(how='all')
            
            # Filtrar columnas Unnamed vacías
            columns_to_keep = []
            for col in self.df.columns:
                if col.startswith('Unnamed:'):
                    if not self.df[col].isna().all() and (self.df[col] != '').any():
                        columns_to_keep.append(col)
                else:
                    columns_to_keep.append(col)
            
            self.df = self.df[columns_to_keep]
            self.file_path = file_path
            
            return True
            
        except Exception as e:
            print(f"Error cargando Excel: {str(e)}")
            return False
    
    def get_available_columns(self) -> List[str]:
        """
        Obtiene lista de columnas disponibles
        
        Returns:
            List[str]: Lista de nombres de columnas
        """
        if self.df is None:
            return []
        
        return list(self.df.columns)
    
    def get_data_with_config(self, config: Dict[str, str]) -> List[Dict]:
        """
        Obtiene datos según configuración de columnas
        
        Args:
            config (Dict): Configuración de columnas
                - 'nombre': Columna de nombres
                - 'grau': Columna de grau
        
        Returns:
            List[Dict]: Lista de registros
        """
        if self.df is None:
            return []
        
        data = []
        
        for idx, row in self.df.iterrows():
            record = {}
            
            if config.get('nombre') and config['nombre'] in self.df.columns:
                val = row[config['nombre']]
                if pd.notna(val):
                    # Convertir a string, removiendo .0 si es número entero
                    if isinstance(val, (int, float)):
                        record[config['nombre']] = str(int(val)) if val == int(val) else str(val)
                    else:
                        record[config['nombre']] = str(val)
                else:
                    record[config['nombre']] = ''
            
            if config.get('grau') and config['grau'] in self.df.columns:
                val = row[config['grau']]
                if pd.notna(val):
                    # Convertir a string, removiendo .0 si es número entero
                    if isinstance(val, (int, float)):
                        record[config['grau']] = str(int(val)) if val == int(val) else str(val)
                    else:
                        record[config['grau']] = str(val)
                else:
                    record[config['grau']] = ''
            
            # Solo agregar si tiene al menos un valor
            if any(record.values()):
                data.append(record)
        
        return data
    
    def get_sheet_names(self) -> List[str]:
        """
        Obtiene nombres de hojas del Excel
        
        Returns:
            List[str]: Lista de nombres de hojas
        """
        if not self.file_path or not os.path.exists(self.file_path):
            return []
        
        try:
            xl_file = pd.ExcelFile(self.file_path)
            return xl_file.sheet_names
        except:
            return []
    
    def get_preview_data(self, max_rows: int = 10) -> Optional[pd.DataFrame]:
        """
        Obtiene vista previa de los datos
        
        Args:
            max_rows (int): Número máximo de filas
            
        Returns:
            pd.DataFrame: DataFrame con preview
        """
        if self.df is None:
            return None
        
        return self.df.head(max_rows)
    
    def get_total_rows(self) -> int:
        """
        Obtiene número total de filas
        
        Returns:
            int: Número de filas
        """
        if self.df is None:
            return 0
        
        return len(self.df)
    
    def validate_columns(self, required_columns: List[str]) -> bool:
        """
        Valida que existan columnas requeridas
        
        Args:
            required_columns (List[str]): Columnas requeridas
            
        Returns:
            bool: True si todas las columnas existen
        """
        if self.df is None:
            return False
        
        return all(col in self.df.columns for col in required_columns)
    
    def get_column_data(self, column_name: str) -> List:
        """
        Obtiene datos de una columna específica
        
        Args:
            column_name (str): Nombre de la columna
            
        Returns:
            List: Lista de valores
        """
        if self.df is None or column_name not in self.df.columns:
            return []
        
        return self.df[column_name].tolist()
