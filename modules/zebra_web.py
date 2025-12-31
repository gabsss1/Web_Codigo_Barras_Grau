"""
Módulo para conexión con impresoras Zebra desde la versión web
Adaptación del módulo original para Streamlit
"""
import win32print
import win32ui
import win32con
from PIL import Image, ImageWin
import io

class ZebraWebPrinter:
    """Clase para manejar impresoras Zebra desde la web"""
    
    def __init__(self):
        self.printer_name = None
        
    def get_available_printers(self):
        """Obtiene lista de impresoras disponibles en el sistema"""
        printers = []
        try:
            # Obtener impresoras locales
            printer_info_local = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            for printer in printer_info_local:
                printers.append(printer[2])
            
            # Obtener impresoras de red/conexiones
            try:
                printer_info_connections = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS)
                for printer in printer_info_connections:
                    if printer[2] not in printers:
                        printers.append(printer[2])
            except:
                pass
                
        except Exception as e:
            print(f"Error obteniendo impresoras: {str(e)}")
        
        return printers
    
    def set_printer(self, printer_name):
        """Establece la impresora a utilizar"""
        self.printer_name = printer_name
        
    def generate_zpl(self, barcode_value, barcode_type='CODE128', nombre=None, grau=None):
        """
        Genera código ZPL para imprimir
        
        Args:
            barcode_value (str): Valor del código de barras
            barcode_type (str): Tipo de código
            nombre (str): Nombre opcional
            grau (str): Grau opcional
            
        Returns:
            str: Código ZPL
        """
        from datetime import datetime
        
        # Mapeo de formatos a códigos ZPL
        zpl_formats = {
            'CODE128': '^BC',
            'CODE39': '^B3',
            'EAN13': '^BE',
            'EAN8': '^B8',
            'UPC_A': '^BU',
            'ITF': '^BI'
        }
        
        zpl_barcode = zpl_formats.get(barcode_type, '^BC')
        
        # Configuración para etiquetas 52mm x 33mm (203 DPI)
        label_width_dots = 415
        label_height_dots = 264
        
        # Código de barras más grande
        barcode_height = 80  # Aumentado de 50 a 80
        barcode_x = 30
        barcode_y = 50
        
        # Obtener fecha actual
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        # Construir ZPL
        zpl = f"""^XA
^PW{label_width_dots}
^LL{label_height_dots}
^FO280,10^A0N,24,24^FD{fecha_actual}^FS
^FO{barcode_x},{barcode_y}
{zpl_barcode}N,{barcode_height},N,N,N,A
^FD{barcode_value}^FS
"""
        
        # Agregar número grande debajo del código de barras
        numero_y = barcode_y + barcode_height + 10
        zpl += f"^FO{barcode_x},{numero_y}^A0N,35,35^FD{barcode_value}^FS\n"
        
        # Agregar nombre debajo del número si existe (tamaño más pequeño para que no se corte)
        if nombre:
            nombre_y = numero_y + 45
            zpl += f"^FO{barcode_x},{nombre_y}^A0N,20,18^FD{nombre}^FS\n"
        
        zpl += "^XZ"
        
        return zpl
    
    def print_barcode(self, barcode_value, barcode_type='CODE128'):
        """
        Imprime un código de barras
        
        Args:
            barcode_value (str): Valor del código
            barcode_type (str): Tipo de código
            
        Returns:
            bool: True si se imprimió correctamente
        """
        if not self.printer_name:
            raise Exception("No hay impresora seleccionada")
        
        try:
            # Generar ZPL
            zpl = self.generate_zpl(barcode_value, barcode_type)
            
            # Enviar a impresora
            hPrinter = win32print.OpenPrinter(self.printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Barcode Label", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, zpl.encode())
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            
            return True
            
        except Exception as e:
            print(f"Error imprimiendo: {str(e)}")
            return False
    
    def print_barcode_with_text(self, barcode_value, barcode_type='CODE128', nombre=None, grau=None):
        """
        Imprime código de barras con texto adicional
        
        Args:
            barcode_value (str): Valor del código
            barcode_type (str): Tipo de código
            nombre (str): Nombre
            grau (str): Grau
            
        Returns:
            bool: True si se imprimió correctamente
        """
        if not self.printer_name:
            raise Exception("No hay impresora seleccionada")
        
        try:
            # Generar ZPL con texto
            zpl = self.generate_zpl(barcode_value, barcode_type, nombre, grau)
            
            # Enviar a impresora
            hPrinter = win32print.OpenPrinter(self.printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Barcode Label", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, zpl.encode())
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            
            return True
            
        except Exception as e:
            print(f"Error imprimiendo con texto: {str(e)}")
            return False
    
    def test_connection(self):
        """
        Prueba la conexión con la impresora
        
        Returns:
            bool: True si la conexión es exitosa
        """
        if not self.printer_name:
            return False
        
        try:
            hPrinter = win32print.OpenPrinter(self.printer_name)
            win32print.ClosePrinter(hPrinter)
            return True
        except:
            return False
