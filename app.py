"""
Aplicación Web - Generador de Códigos de Barras para Impresoras Zebra
Versión web de la aplicación de escritorio usando Streamlit
"""
import streamlit as st
import sys
import os

# Agregar directorios al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.barcode_web import BarcodeWebGenerator
from modules.zebra_web import ZebraWebPrinter
from modules.excel_web import ExcelWebReader
from PIL import Image
import io
import zipfile
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Generador de Códigos de Barras - Zebra",
    page_icon="�️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'barcode_generator' not in st.session_state:
    st.session_state.barcode_generator = BarcodeWebGenerator()
if 'zebra_printer' not in st.session_state:
    st.session_state.zebra_printer = ZebraWebPrinter()
if 'excel_reader' not in st.session_state:
    st.session_state.excel_reader = ExcelWebReader()
if 'current_barcodes' not in st.session_state:
    st.session_state.current_barcodes = []
if 'excel_mode' not in st.session_state:
    st.session_state.excel_mode = False
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None
if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = set()
if 'print_double' not in st.session_state:
    st.session_state.print_double = False

def main():
    """Función principal de la aplicación"""
    
    # Título principal
    st.title("Generador de Códigos de Barras - Zebra Printer")
    st.markdown("---")
    
    # Sidebar - Configuración
    with st.sidebar:
        st.header("Configuración")
        
        # Configuración de código de barras
        st.subheader("Configuración de Código")
        
        barcode_format = st.selectbox(
            "Formato de Código:",
            st.session_state.barcode_generator.get_supported_formats(),
            index=0
        )
        
        format_template = st.text_input(
            "Formato de Número:",
            value="{}.01",
            help="Ejemplo: {}.01 = 1.01, 2.01... | {} = 1, 2..."
        )
        
        # Opción de impresión doble
        print_double = st.checkbox(
            "Imprimir cada código 2 veces",
            value=st.session_state.print_double,
            help="Cada código de barras se imprimirá duplicado"
        )
        st.session_state.print_double = print_double
        
        st.markdown("---")
        
        # Configuración de impresora
        st.subheader("Impresora Zebra")
        
        printers = st.session_state.zebra_printer.get_available_printers()
        
        if printers:
            selected_printer = st.selectbox(
                "Selecciona la impresora:",
                printers,
                key="printer_select",
                help="Selecciona la impresora Zebra donde deseas imprimir"
            )
            st.session_state.zebra_printer.set_printer(selected_printer)
            
            # Mostrar impresora seleccionada de forma destacada
            st.markdown(f"""
                <div style='padding: 10px; background-color: #d4edda; border-radius: 5px; border-left: 4px solid #28a745;'>
                    <strong>Impresora activa:</strong><br>
                    <code>{selected_printer}</code>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("No se encontraron impresoras")
            st.info("Verifica que la impresora Zebra esté instalada y encendida")
            selected_printer = None
        
        if st.button("Actualizar lista de impresoras"):
            st.rerun()
    
    # Contenido principal - Modo Excel
    render_excel_mode(barcode_format, format_template)

def render_excel_mode(barcode_format, format_template):
    """Renderiza el modo Excel"""
    
    st.header("Generador de Códigos - Importar desde Excel")
    
    # Upload de archivo
    uploaded_file = st.file_uploader(
        "Cargar archivo Excel",
        type=['xlsx', 'xls'],
        help="Sube un archivo Excel con los datos"
    )
    
    if uploaded_file is not None:
        # Guardar temporalmente el archivo
        temp_path = os.path.join("web_app", "temp", uploaded_file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Obtener hojas disponibles
        temp_reader = ExcelWebReader()
        temp_reader.file_path = temp_path
        sheet_names = temp_reader.get_sheet_names()
        
        # Selector de hoja de Excel
        st.subheader("Configuración de lectura")
        
        if len(sheet_names) > 1:
            selected_sheet = st.selectbox(
                "Selecciona la hoja de Excel:",
                sheet_names,
                help="El archivo tiene múltiples hojas, selecciona la que deseas usar"
            )
            st.info(f"Hoja seleccionada: **{selected_sheet}**")
        else:
            selected_sheet = sheet_names[0] if sheet_names else None
            if selected_sheet:
                st.info(f"Usando hoja: **{selected_sheet}**")
        
        header_row = st.number_input(
            "Fila de encabezado (primera fila = 1):",
            min_value=1,
            max_value=20,
            value=1,
            help="Si los encabezados están en otra fila, ajusta este valor"
        )
        
        # Cargar Excel con fila de encabezado personalizada
        if st.session_state.excel_reader.load_excel_with_header(temp_path, header_row - 1, selected_sheet):
            st.success(f"Archivo Excel cargado correctamente - Hoja: {selected_sheet}")
            
            # Obtener columnas disponibles
            columns = st.session_state.excel_reader.get_available_columns()
            
            st.subheader("Selecciona las columnas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_col = st.selectbox(
                    "Columna APELLIDOS Y NOMBRES:",
                    [""] + columns,
                    key="nombre_col"
                )
            
            with col2:
                grau_col = st.selectbox(
                    "Columna GRAU:",
                    [""] + columns,
                    key="grau_col"
                )
            
            # Mostrar vista previa de datos
            if nombre_col and grau_col:
                st.markdown("---")
                st.subheader("Vista Previa de Datos")
                
                config = {
                    'nombre': nombre_col,
                    'grau': grau_col
                }
                
                data = st.session_state.excel_reader.get_data_with_config(config)
                
                if data:
                    # Mostrar preview visual de cada orden
                    st.info(f"Total de registros encontrados: **{len(data)}**")
                    
                    # Tabla completa expandible
                    with st.expander("Ver tabla completa"):
                        st.dataframe(data)
                    
                    # Selección de filas
                    st.subheader("Seleccionar Registros")
                    
                    selection_mode = st.radio(
                        "Modo de selección:",
                        ["Todos", "Rango"],
                        horizontal=True
                    )
                    
                    selected_indices = []
                    
                    if selection_mode == "Todos":
                        selected_indices = list(range(len(data)))
                    elif selection_mode == "Rango":
                        col1, col2 = st.columns(2)
                        with col1:
                            start_row = st.number_input("Desde fila:", 1, len(data), 1)
                        with col2:
                            end_row = st.number_input("Hasta fila:", 1, len(data), min(10, len(data)))
                        
                        if start_row <= end_row:
                            selected_indices = list(range(start_row - 1, end_row))
                    
                    if selected_indices:
                        st.info(f"Seleccionados: **{len(selected_indices)}** registros")
                        
                        # Botones de acción
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("Vista Previa", key="excel_preview_btn"):
                                generate_excel_preview(data, selected_indices, config, barcode_format)
                        
                        with col2:
                            if st.button("Imprimir", key="excel_print_btn"):
                                print_excel_barcodes(data, selected_indices, config, barcode_format)
                        
                        with col3:
                            if st.button("Descargar ZIP", key="excel_download_btn"):
                                download_excel_zip(data, selected_indices, config, barcode_format)
        
        # Limpiar archivo temporal
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
    
    # Mostrar vista previa si existe
    if st.session_state.current_barcodes:
        st.markdown("---")
        st.subheader("Vista Previa de Códigos")
        display_preview()

def generate_excel_preview(data, selected_indices, config, barcode_format):
    """Genera vista previa desde datos Excel"""
    try:
        with st.spinner("Generando vista previa desde Excel..."):
            barcodes = []
            for idx in selected_indices:
                row = data[idx]
                
                # Obtener valores
                nombre = row.get(config.get('nombre'), '') if config.get('nombre') else ''
                grau = row.get(config.get('grau'), '') if config.get('grau') else ''
                
                # Generar código con formato grau.01
                code = f"{grau}.01" if grau else f"{idx+1}.01"
                
                img = st.session_state.barcode_generator.generate_barcode_with_text(
                    barcode_format,
                    code,
                    nombre,
                    str(grau)
                )
                
                barcodes.append({
                    'number': idx + 1,
                    'code': code,
                    'nombre': nombre,
                    'grau': grau,
                    'image': img
                })
            
            st.session_state.current_barcodes = barcodes
            st.success(f"{len(barcodes)} códigos generados desde Excel")
    except Exception as e:
        st.error(f"Error generando códigos: {str(e)}")

def display_preview(filter_range=None):
    """Muestra la vista previa de códigos"""
    barcodes = st.session_state.current_barcodes
    
    if not barcodes:
        return
    
    barcodes_to_show = barcodes
    
    # Mostrar en grid
    cols_per_row = 3
    for i in range(0, len(barcodes_to_show), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(barcodes_to_show):
                barcode = barcodes_to_show[i + j]
                with cols[j]:
                    st.image(barcode['image'], caption=f"Código: {barcode['code']}")
                    if 'nombre' in barcode:
                        st.caption(f"{barcode['nombre']}")

def print_excel_barcodes(data, selected_indices, config, barcode_format):
    """Imprime códigos desde Excel"""
    try:
        printer = st.session_state.zebra_printer
        
        if not printer.printer_name:
            st.error("No hay impresora seleccionada")
            return
        
        # Determinar cuántas veces imprimir cada código
        copies = 2 if st.session_state.print_double else 1
        total_prints = len(selected_indices) * copies
        
        with st.spinner(f"Imprimiendo {total_prints} etiquetas ({len(selected_indices)} códigos x {copies})..."):
            success_count = 0
            for idx in selected_indices:
                row = data[idx]
                
                nombre = row.get(config.get('nombre'), '') if config.get('nombre') else ''
                grau = row.get(config.get('grau'), '') if config.get('grau') else ''
                
                code = f"{grau}.01" if grau else f"{idx+1}.01"
                
                # Imprimir las copias necesarias
                for copy in range(copies):
                    if printer.print_barcode_with_text(code, barcode_format, nombre, str(grau)):
                        success_count += 1
            
            if success_count == total_prints:
                st.success(f"{success_count} etiquetas impresas correctamente ({len(selected_indices)} códigos x {copies})")
            else:
                st.warning(f"Se imprimieron {success_count} de {total_prints} etiquetas")
    except Exception as e:
        st.error(f"Error imprimiendo: {str(e)}")

def download_excel_zip(data, selected_indices, config, barcode_format):
    """Descarga códigos Excel como ZIP"""
    try:
        with st.spinner("Preparando descarga..."):
            zip_buffer = io.BytesIO()
            copies = 2 if st.session_state.print_double else 1
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for idx in selected_indices:
                    row = data[idx]
                    
                    nombre = row.get(config.get('nombre'), '') if config.get('nombre') else ''
                    grau = row.get(config.get('grau'), '') if config.get('grau') else ''
                    
                    code = f"{grau}.01" if grau else f"{idx+1}.01"
                    
                    img = st.session_state.barcode_generator.generate_barcode_with_text(
                        barcode_format,
                        code,
                        nombre,
                        str(grau)
                    )
                    
                    # Convertir imagen a bytes
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    img_bytes = img_buffer.getvalue()
                    
                    # Agregar al ZIP (duplicado si es necesario)
                    safe_name = nombre.replace(' ', '_').replace('/', '_')[:50] if nombre else f"orden_{idx+1}"
                    for copy in range(copies):
                        suffix = f"_copia{copy+1}" if copies > 1 else ""
                        zip_file.writestr(f"barcode_{safe_name}_{code}{suffix}.png", img_bytes)
            
            zip_buffer.seek(0)
            
            # Descargar
            st.download_button(
                label="Descargar ZIP",
                data=zip_buffer,
                file_name=f"barcodes_excel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
            
            st.success("ZIP preparado para descarga")
    except Exception as e:
        st.error(f"Error preparando descarga: {str(e)}")

def parse_range_string(range_str, max_value):
    """
    Parsea string de rangos (ej: "1,3,5-10") a lista de índices
    
    Args:
        range_str: String con rangos
        max_value: Valor máximo permitido
    
    Returns:
        Lista de índices (0-based)
    """
    indices = set()
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Rango
            start, end = part.split('-')
            start = int(start.strip())
            end = int(end.strip())
            indices.update(range(start - 1, min(end, max_value)))
        else:
            # Número individual
            num = int(part.strip())
            if 1 <= num <= max_value:
                indices.add(num - 1)
    
    return sorted(list(indices))

if __name__ == "__main__":
    main()
