"""
Generador de códigos de barras para la versión web
Adaptación del generador original para Streamlit
"""
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os

class BarcodeWebGenerator:
    """Clase para generar códigos de barras en la versión web"""
    
    def __init__(self):
        self.supported_formats = {
            'CODE128': barcode.Code128,
            'CODE39': barcode.Code39,
            'EAN13': barcode.EAN13,
            'EAN8': barcode.EAN8,
            'UPC_A': barcode.UPCA,
            'ITF': barcode.ITF
        }
    
    def get_supported_formats(self):
        """Retorna lista de formatos soportados"""
        return list(self.supported_formats.keys())
    
    def generate_barcode(self, format_type, code_value, width=2, height=15):
        """
        Genera un código de barras
        
        Args:
            format_type (str): Tipo de código de barras
            code_value (str): Valor a codificar
            width (int): Ancho de las barras
            height (int): Alto de las barras en mm
            
        Returns:
            PIL.Image: Imagen del código de barras
        """
        try:
            if format_type not in self.supported_formats:
                raise ValueError(f"Formato no soportado: {format_type}")
            
            # Configurar el generador de códigos de barras
            barcode_class = self.supported_formats[format_type]
            
            # Configurar las opciones del writer
            writer = ImageWriter()
            writer.set_options({
                'module_width': width / 10,
                'module_height': height,
                'quiet_zone': 6.5,
                'font_size': 10,
                'text_distance': 5,
                'background': 'white',
                'foreground': 'black',
                'write_text': True,
            })
            
            # Generar el código de barras
            barcode_instance = barcode_class(str(code_value), writer=writer)
            
            # Guardar en buffer
            buffer = BytesIO()
            barcode_instance.write(buffer)
            buffer.seek(0)
            
            # Convertir a imagen PIL
            image = Image.open(buffer)
            
            return image
            
        except Exception as e:
            raise Exception(f"Error generando código de barras: {str(e)}")
    
    def generate_barcode_with_text(self, format_type, code_value, nombre=None, grau=None):
        """
        Genera código de barras con texto adicional (nombre y grau)
        
        Args:
            format_type (str): Tipo de código de barras
            code_value (str): Valor del código
            nombre (str): Nombre de la persona
            grau (str): Grau/grado
            
        Returns:
            PIL.Image: Imagen del código con texto
        """
        try:
            # Generar código de barras base
            barcode_img = self.generate_barcode(format_type, code_value)
            
            # Si no hay texto adicional, retornar solo el código
            if not nombre and not grau:
                return barcode_img
            
            # Crear imagen más grande para incluir texto
            width, height = barcode_img.size
            additional_height = 0
            
            if nombre:
                additional_height += 30
            if grau:
                additional_height += 25
            
            # Crear nueva imagen
            new_img = Image.new('RGB', (width, height + additional_height), 'white')
            
            # Pegar código de barras
            new_img.paste(barcode_img, (0, 0))
            
            # Agregar texto
            draw = ImageDraw.Draw(new_img)
            
            try:
                # Intentar usar fuente del sistema
                font_large = ImageFont.truetype("arial.ttf", 14)
                font_small = ImageFont.truetype("arial.ttf", 12)
            except:
                # Usar fuente por defecto
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            y_position = height + 5
            
            if nombre:
                # Centrar texto del nombre
                text = f"Nombre: {nombre}"
                bbox = draw.textbbox((0, 0), text, font=font_large)
                text_width = bbox[2] - bbox[0]
                x_position = (width - text_width) // 2
                draw.text((x_position, y_position), text, fill='black', font=font_large)
                y_position += 25
            
            if grau:
                # Centrar texto del grau
                text = f"Grau: {grau}"
                bbox = draw.textbbox((0, 0), text, font=font_small)
                text_width = bbox[2] - bbox[0]
                x_position = (width - text_width) // 2
                draw.text((x_position, y_position), text, fill='black', font=font_small)
            
            return new_img
            
        except Exception as e:
            raise Exception(f"Error generando código con texto: {str(e)}")
    
    def generate_barcode_bytes(self, format_type, code_value):
        """
        Genera código de barras y retorna como bytes (para descarga)
        
        Args:
            format_type (str): Tipo de código de barras
            code_value (str): Valor del código
            
        Returns:
            bytes: Imagen en formato PNG
        """
        img = self.generate_barcode(format_type, code_value)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
