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
from modules.ordenes_nexlab import OrdenesNexlab
from PIL import Image
import io
from datetime import datetime
import json

# Configuración de la página
st.set_page_config(
    page_title="EMERGENCIAS GRAU - CODIGO DE BARRAS",
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

# Archivo de configuración
CONFIG_FILE = os.path.join("web_app", "temp", "printer_config.json")

def save_printer_config(printer_name):
    """Guarda la configuración de la impresora seleccionada"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'printer_name': printer_name}, f)
        return True
    except Exception as e:
        st.error(f"Error guardando configuración: {str(e)}")
        return False

def load_printer_config():
    """Carga la configuración de la impresora guardada"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('printer_name')
    except Exception as e:
        pass
    return None

# Inicializar session state
if 'barcode_generator' not in st.session_state:
    st.session_state.barcode_generator = BarcodeWebGenerator()
if 'zebra_printer' not in st.session_state:
    st.session_state.zebra_printer = ZebraWebPrinter()
if 'excel_reader' not in st.session_state:
    st.session_state.excel_reader = ExcelWebReader()
if 'ordenes_nexlab' not in st.session_state:
    st.session_state.ordenes_nexlab = OrdenesNexlab()
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
if 'selected_barcodes' not in st.session_state:
    st.session_state.selected_barcodes = set()
if 'search_filter' not in st.session_state:
    st.session_state.search_filter = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'items_per_page' not in st.session_state:
    st.session_state.items_per_page = 12
if 'saved_printer' not in st.session_state:
    st.session_state.saved_printer = load_printer_config()

def main():
    """Función principal de la aplicación"""
    
    # Encabezado con logos
    col_logo1, col_title, col_logo2 = st.columns([1, 3, 1])
    
    with col_logo1:
        try:
            st.image("assets/logo.png", width=150)
        except:
            pass
    
    with col_title:
        st.title("Generador de Códigos de Barras")
        st.subheader("Emergencias Grau")
    
    with col_logo2:
        try:
            st.image("assets/essalud_logo.png", width=150)
        except:
            pass
    
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
            # Intentar seleccionar la impresora guardada si está disponible
            default_index = 0
            if st.session_state.saved_printer and st.session_state.saved_printer in printers:
                default_index = printers.index(st.session_state.saved_printer)
            
            selected_printer = st.selectbox(
                "Selecciona la impresora:",
                printers,
                index=default_index,
                key="printer_select",
                help="Selecciona la impresora Zebra donde deseas imprimir"
            )
            st.session_state.zebra_printer.set_printer(selected_printer)
            
            # Botón para guardar la impresora seleccionada
            if st.button("Guardar impresora"):
                if save_printer_config(selected_printer):
                    st.session_state.saved_printer = selected_printer
                    st.success(f"Impresora guardada: {selected_printer}")
                    st.rerun()
            
            # Mostrar impresora seleccionada de forma destacada
            saved_indicator = " (Guardada)" if selected_printer == st.session_state.saved_printer else ""
            st.markdown(f"""
                <div style='padding: 10px; background-color: #d4edda; border-radius: 5px; border-left: 4px solid #28a745;'>
                    <strong>Impresora activa:</strong><br>
                    <code>{selected_printer}{saved_indicator}</code>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("No se encontraron impresoras")
            st.info("Verifica que la impresora Zebra esté instalada y encendida")
            selected_printer = None
        
        if st.button("Actualizar lista de impresoras"):
            st.rerun()
    
    # Contenido principal - Selector de modo
    st.header("Modo de Ingreso")
    
    mode = st.radio(
        "Selecciona el método de ingreso:",
        ["Ingreso Manual", "Importar desde Excel", "Búsqueda por Orden (Nexlab)"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if mode == "Ingreso Manual":
        render_manual_mode(barcode_format, format_template)
    elif mode == "Importar desde Excel":
        render_excel_mode(barcode_format, format_template)
    else:
        render_nexlab_mode(barcode_format)

def render_manual_mode(barcode_format, format_template):
    """Renderiza el modo de ingreso manual"""
    
    st.header("Generador de Códigos - Ingreso Manual")
    
    # Inicializar lista de códigos manuales en session_state
    if 'manual_entries' not in st.session_state:
        st.session_state.manual_entries = []
    
    st.subheader("Agregar Nueva Etiqueta")
    
    col1, col2 = st.columns(2)
    
    with col1:
        grau_input = st.text_input(
            "Número de Orden (GRAU):",
            key="grau_manual_input",
            placeholder="Ejemplo: 12345",
            help="Ingresa el número de orden GRAU"
        )
    
    with col2:
        nombre_input = st.text_input(
            "Apellidos y Nombres:",
            key="nombre_manual_input",
            placeholder="Ejemplo: GARCIA PEREZ JUAN",
            help="Ingresa los apellidos y nombres completos"
        )
    
    # Botón para agregar entrada
    if st.button("Agregar a la lista", key="add_manual_btn"):
        if grau_input.strip() and nombre_input.strip():
            # Agregar a la lista
            st.session_state.manual_entries.append({
                'grau': grau_input.strip(),
                'nombre': nombre_input.strip().upper()
            })
            st.success(f"Agregado: GRAU {grau_input} - {nombre_input.upper()}")
            st.rerun()
        else:
            st.error("Por favor, completa ambos campos (GRAU y Nombre)")
    
    # Mostrar lista de entradas
    if st.session_state.manual_entries:
        st.markdown("---")
        st.subheader("Lista de Etiquetas")
        
        st.info(f"Total de etiquetas en la lista: **{len(st.session_state.manual_entries)}**")
        
        # Tabla con las entradas
        for idx, entry in enumerate(st.session_state.manual_entries):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"**{idx + 1}.**")
            
            with col2:
                st.markdown(f"**GRAU:** {entry['grau']} | **Nombre:** {entry['nombre']}")
            
            with col3:
                if st.button("Eliminar", key=f"delete_manual_{idx}", help="Eliminar"):
                    st.session_state.manual_entries.pop(idx)
                    st.rerun()
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Vista Previa", key="manual_preview_btn"):
                generate_manual_preview(st.session_state.manual_entries, barcode_format, format_template)
        
        with col2:
            if st.button("Limpiar Lista", key="clear_manual_btn"):
                st.session_state.manual_entries = []
                st.session_state.current_barcodes = []
                st.session_state.selected_barcodes = set()
                st.rerun()
        
        with col3:
            st.write("")  # Espaciador
    
    # Mostrar vista previa si existe
    if st.session_state.current_barcodes:
        st.markdown("---")
        st.subheader("Vista Previa de Códigos")
        display_preview()
        
        # Botones de acción para etiquetas seleccionadas
        if st.session_state.selected_barcodes:
            st.markdown("---")
            st.subheader("Acciones con Seleccionadas")
            
            if st.button("Imprimir Seleccionadas", key="print_selected_manual_btn"):
                print_selected_barcodes(barcode_format)

def generate_manual_preview(entries, barcode_format, format_template):
    """Genera vista previa desde entradas manuales"""
    try:
        with st.spinner("Generando vista previa..."):
            barcodes = []
            for idx, entry in enumerate(entries):
                grau = entry.get('grau', '')
                nombre = entry.get('nombre', '').upper()
                
                # Generar código usando el formato template
                code = format_template.replace('{}', str(grau))
                
                img = st.session_state.barcode_generator.generate_barcode_with_text(
                    barcode_format,
                    code,
                    nombre,
                    str(grau)
                )
                
                barcodes.append({
                    'id': idx + 1,
                    'number': idx + 1,
                    'code': code,
                    'nombre': nombre,
                    'grau': grau,
                    'image': img
                })
            
            st.session_state.current_barcodes = barcodes
            st.success(f"{len(barcodes)} códigos generados correctamente")
    except Exception as e:
        st.error(f"Error generando códigos: {str(e)}")

def generate_nexlab_preview(entries, barcode_format):
    """Genera vista previa desde órdenes Nexlab"""
    try:
        with st.spinner("Generando vista previa..."):
            barcodes = []
            for idx, entry in enumerate(entries):
                codigo = entry.get('codigo', '')
                nombre = entry.get('nombre', '').upper()
                sexo = entry.get('sexo', '')
                orden_numero = entry.get('orden_numero', '')
                
                # Generar código de barras
                img = st.session_state.barcode_generator.generate_barcode(
                    barcode_format,
                    codigo,
                    width=2,
                    height=15
                )
                
                barcodes.append({
                    'id': idx + 1,
                    'number': idx + 1,
                    'code': codigo,
                    'nombre': nombre,
                    'sexo': sexo,
                    'orden_numero': orden_numero,
                    'image': img
                })
            
            st.session_state.current_barcodes = barcodes
            st.success(f"{len(barcodes)} códigos generados correctamente")
    except Exception as e:
        st.error(f"Error generando códigos: {str(e)}")

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
        try:
            # Guardar temporalmente el archivo
            temp_path = os.path.join("web_app", "temp", uploaded_file.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            # Asegurar que el archivo se escriba completamente
            uploaded_file.seek(0)  # Resetear el puntero al inicio
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            
            # Verificar que el archivo se guardó correctamente
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                st.error("Error al guardar el archivo temporalmente")
                return
            
            # Obtener hojas disponibles
            temp_reader = ExcelWebReader()
            temp_reader.file_path = temp_path
            sheet_names = temp_reader.get_sheet_names()
        except Exception as e:
            st.error(f"Error cargando Excel: {str(e)}")
            st.info("Verifica que el archivo sea un Excel válido (.xlsx o .xls)")
            return
        
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
                        
                        # Botón de vista previa
                        if st.button("Vista Previa", key="excel_preview_btn"):
                            generate_excel_preview(data, selected_indices, config, barcode_format)
        
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
        
        # Botones de acción para etiquetas seleccionadas
        if st.session_state.selected_barcodes:
            st.markdown("---")
            st.subheader("Acciones con Seleccionadas")
            
            if st.button("Imprimir Seleccionadas", key="print_selected_btn"):
                print_selected_barcodes(barcode_format)

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
                    'id': idx + 1,
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
    """Muestra la vista previa de códigos con búsqueda y selección"""
    barcodes = st.session_state.current_barcodes
    
    if not barcodes:
        return
    
    # Barra de búsqueda y herramientas
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        search_text = st.text_input(
            "Buscar etiqueta",
            value=st.session_state.search_filter,
            placeholder="Buscar por ID, código, nombre o GRAU...",
            key="search_input"
        )
        if search_text != st.session_state.search_filter:
            st.session_state.search_filter = search_text
            st.session_state.current_page = 1
    
    with col2:
        if st.button("Seleccionar Todo"):
            # Seleccionar todos los índices filtrados
            barcodes_to_select = []
            if search_text.strip():
                search_lower = search_text.lower().strip()
                for idx, barcode in enumerate(barcodes):
                    if (search_lower in str(barcode.get('id', '')).lower() or
                        search_lower in str(barcode.get('code', '')).lower() or
                        search_lower in str(barcode.get('nombre', '')).lower() or
                        search_lower in str(barcode.get('grau', '')).lower()):
                        barcodes_to_select.append(idx)
            else:
                barcodes_to_select = list(range(len(barcodes)))
            st.session_state.selected_barcodes = set(barcodes_to_select)
            st.rerun()
    
    with col3:
        if st.button("Deseleccionar Todo"):
            st.session_state.selected_barcodes = set()
            st.rerun()
    
    with col4:
        if st.button("Limpiar Vista"):
            st.session_state.current_barcodes = []
            st.session_state.selected_barcodes = set()
            st.session_state.search_filter = ""
            st.rerun()
    
    # Filtrar etiquetas según búsqueda (optimizado)
    barcodes_to_show = []
    if search_text.strip():
        search_lower = search_text.lower().strip()
        for idx, barcode in enumerate(barcodes):
            # Buscar en ID, código, nombre y grau (optimizado con 'in')
            if (search_lower in str(barcode.get('id', '')).lower() or
                search_lower in str(barcode.get('code', '')).lower() or
                search_lower in str(barcode.get('nombre', '')).lower() or
                search_lower in str(barcode.get('grau', '')).lower()):
                barcodes_to_show.append((idx, barcode))
    else:
        barcodes_to_show = [(idx, barcode) for idx, barcode in enumerate(barcodes)]
    
    total_filtered = len(barcodes_to_show)
    
    # Mostrar todas las etiquetas sin paginación
    current_page_items = barcodes_to_show
    
    # Mostrar contador
    if search_text.strip():
        st.info(f"Mostrando {total_filtered} de {len(barcodes)} etiquetas | {len(st.session_state.selected_barcodes)} seleccionadas")
    else:
        st.info(f"Total: {len(barcodes)} etiquetas | {len(st.session_state.selected_barcodes)} seleccionadas")
    
    if not current_page_items:
        st.warning("No se encontraron etiquetas que coincidan con la búsqueda")
        return
    
    # Mostrar en grid con selección simple
    cols_per_row = 3
    for i in range(0, len(current_page_items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(current_page_items):
                idx, barcode = current_page_items[i + j]
                with cols[j]:
                    # ID y selector
                    st.markdown(f"**ID: {barcode.get('id', idx+1)}**")
                    
                    # Input simple de selección (0 o 1)
                    select_key = f"select_{idx}"
                    
                    # Si el valor no está en session_state para esta key, inicializarlo
                    if select_key not in st.session_state:
                        st.session_state[select_key] = 1 if idx in st.session_state.selected_barcodes else 0
                    
                    # Sincronizar el valor del widget con selected_barcodes
                    st.session_state[select_key] = 1 if idx in st.session_state.selected_barcodes else 0
                    
                    selected = st.number_input(
                        "Seleccionar:",
                        min_value=0,
                        max_value=1,
                        value=st.session_state[select_key],
                        step=1,
                        key=select_key,
                        help="0 = No seleccionar, 1 = Seleccionar"
                    )
                    
                    # Agregar/quitar de selected_barcodes según el valor
                    if selected == 1:
                        st.session_state.selected_barcodes.add(idx)
                    else:
                        st.session_state.selected_barcodes.discard(idx)
                    
                    # Imagen de la etiqueta
                    st.image(barcode['image'], use_container_width=True)
                    
                    # Información de la etiqueta
                    st.caption(f"Código: {barcode['code']}")
                    if 'nombre' in barcode and barcode['nombre']:
                        st.caption(f"Nombre: {barcode['nombre']}")
                    if 'grau' in barcode and barcode['grau']:
                        st.caption(f"GRAU: {barcode['grau']}")

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

def print_selected_barcodes(barcode_format):
    """Imprime solo las etiquetas seleccionadas"""
    try:
        printer = st.session_state.zebra_printer
        
        if not printer.printer_name:
            st.error("No hay impresora seleccionada")
            return
        
        selected_indices = sorted(list(st.session_state.selected_barcodes))
        barcodes = st.session_state.current_barcodes
        
        if not selected_indices:
            st.warning("No hay etiquetas seleccionadas")
            return
        
        # Determinar cuántas veces imprimir cada código
        copies = 2 if st.session_state.print_double else 1
        total_prints = len(selected_indices) * copies
        
        with st.spinner(f"Imprimiendo {total_prints} etiquetas ({len(selected_indices)} códigos x {copies})..."):
            success_count = 0
            for idx in selected_indices:
                barcode = barcodes[idx]
                
                code = barcode.get('code', '')
                nombre = barcode.get('nombre', '')
                grau = str(barcode.get('grau', ''))
                
                # Imprimir las copias necesarias
                for copy in range(copies):
                    if printer.print_barcode_with_text(code, barcode_format, nombre, grau):
                        success_count += 1
            
            if success_count == total_prints:
                st.success(f"{success_count} etiquetas impresas correctamente ({len(selected_indices)} códigos x {copies})")
            else:
                st.warning(f"Se imprimieron {success_count} de {total_prints} etiquetas")
    except Exception as e:
        st.error(f"Error imprimiendo: {str(e)}")

def print_selected_nexlab_barcodes(barcode_format):
    """Imprime solo las etiquetas seleccionadas de Nexlab"""
    try:
        printer = st.session_state.zebra_printer
        
        if not printer.printer_name:
            st.error("No hay impresora seleccionada")
            return
        
        selected_indices = sorted(list(st.session_state.selected_barcodes))
        barcodes = st.session_state.current_barcodes
        
        if not selected_indices:
            st.warning("No hay etiquetas seleccionadas")
            return
        
        # Determinar cuántas veces imprimir cada código
        copies = 2 if st.session_state.print_double else 1
        total_prints = len(selected_indices) * copies
        
        with st.spinner(f"Imprimiendo {total_prints} etiquetas ({len(selected_indices)} códigos x {copies})..."):
            success_count = 0
            for idx in selected_indices:
                barcode = barcodes[idx]
                
                code = barcode.get('code', '')
                nombre = barcode.get('nombre', '')
                sexo = barcode.get('sexo', '')
                
                # Imprimir las copias necesarias
                for copy in range(copies):
                    # Generar ZPL con sexo incluido
                    zpl = printer.generate_zpl(code, barcode_format, nombre=nombre, grau=None, sexo=sexo)
                    if printer.send_to_printer(zpl):
                        success_count += 1
            
            if success_count == total_prints:
                st.success(f"✅ {success_count} etiquetas impresas correctamente ({len(selected_indices)} códigos x {copies})")
            else:
                st.warning(f"⚠️ Se imprimieron {success_count} de {total_prints} etiquetas")
    except Exception as e:
        st.error(f"❌ Error imprimiendo: {str(e)}")

def download_selected_barcodes(barcode_format):
    """Descarga solo las etiquetas seleccionadas como ZIP"""
    try:
        selected_indices = sorted(list(st.session_state.selected_barcodes))
        barcodes = st.session_state.current_barcodes
        
        if not selected_indices:
            st.warning("No hay etiquetas seleccionadas")
            return
        
        with st.spinner("Preparando descarga..."):
            zip_buffer = io.BytesIO()
            copies = 2 if st.session_state.print_double else 1
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for idx in selected_indices:
                    barcode = barcodes[idx]
                    
                    code = barcode.get('code', '')
                    nombre = barcode.get('nombre', '')
                    img = barcode.get('image')
                    
                    if img:
                        # Convertir imagen a bytes
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG')
                        img_bytes = img_buffer.getvalue()
                        
                        # Agregar al ZIP (duplicado si es necesario)
                        safe_name = nombre.replace(' ', '_').replace('/', '_')[:50] if nombre else f"etiqueta_{idx+1}"
                        for copy in range(copies):
                            suffix = f"_copia{copy+1}" if copies > 1 else ""
                            zip_file.writestr(f"barcode_ID{barcode.get('id', idx+1)}_{safe_name}_{code}{suffix}.png", img_bytes)
            
            zip_buffer.seek(0)
            
            # Descargar
            st.download_button(
                label="Descargar ZIP de Seleccionadas",
                data=zip_buffer,
                file_name=f"barcodes_seleccionadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                key="download_selected_zip"
            )
            
            st.success(f"ZIP preparado con {len(selected_indices)} etiquetas (x{copies} copias c/u)")
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

def render_nexlab_mode(barcode_format):
    """Renderiza el modo de búsqueda de órdenes Nexlab"""
    
    st.header("Búsqueda de Órdenes - Nexlab")
    
    # Inicializar lista de órdenes Nexlab en session_state
    if 'nexlab_entries' not in st.session_state:
        st.session_state.nexlab_entries = []
    
    st.subheader("Buscar y Agregar Órdenes")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        numero_orden = st.text_input(
            "Número de Orden:",
            key="nexlab_orden_input",
            placeholder="Ejemplo: 1622485",
            help="Ingresa el número de orden a buscar"
        )
    
    with col2:
        st.write("")  # Espaciador
        st.write("")  # Espaciador
        buscar_btn = st.button("🔍 Buscar y Agregar", type="primary", use_container_width=True)
    
    # Procesar búsqueda
    if buscar_btn and numero_orden:
        with st.spinner(f"Buscando orden {numero_orden}..."):
            exito, resultado = st.session_state.ordenes_nexlab.buscar_orden(numero_orden)
            
            if exito:
                # Generar datos de la etiqueta
                etiqueta_data = st.session_state.ordenes_nexlab.generar_etiqueta_texto(resultado)
                
                # Verificar si ya está en la lista
                ya_existe = any(entry['orden_numero'] == resultado['numero_orden'] 
                               for entry in st.session_state.nexlab_entries)
                
                if not ya_existe:
                    # Agregar a la lista
                    st.session_state.nexlab_entries.append({
                        'orden_numero': resultado['numero_orden'],
                        'codigo': etiqueta_data['codigo'],
                        'nombre': etiqueta_data['nombre'],
                        'sexo': etiqueta_data['sexo'],
                        'fecha': etiqueta_data['fecha'],
                        'estado': resultado['estado']
                    })
                    st.success(f"✅ Orden {resultado['numero_orden']} agregada a la lista")
                    st.rerun()
                else:
                    st.warning(f"⚠️ La orden {resultado['numero_orden']} ya está en la lista")
            
            else:
                st.error(f"❌ {resultado}")
                st.info("Verifica que el número de orden sea correcto")
    
    elif buscar_btn and not numero_orden:
        st.warning("⚠️ Por favor ingresa un número de orden")
    
    # Mostrar lista de órdenes agregadas
    if st.session_state.nexlab_entries:
        st.markdown("---")
        st.subheader("Lista de Órdenes")
        
        st.info(f"Total de órdenes en la lista: **{len(st.session_state.nexlab_entries)}**")
        
        # Tabla con las entradas
        for idx, entry in enumerate(st.session_state.nexlab_entries):
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.markdown(f"**{idx + 1}.**")
            
            with col2:
                st.markdown(f"**Orden:** {entry['codigo']} | **Nombre:** {entry['nombre']} | **Sexo:** {entry['sexo']}")
            
            with col3:
                if st.button("🗑️", key=f"delete_nexlab_{idx}", help="Eliminar"):
                    st.session_state.nexlab_entries.pop(idx)
                    st.rerun()
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Vista Previa", key="nexlab_preview_btn", use_container_width=True):
                generate_nexlab_preview(st.session_state.nexlab_entries, barcode_format)
        
        with col2:
            if st.button("🗑️ Limpiar Lista", key="clear_nexlab_btn", use_container_width=True):
                st.session_state.nexlab_entries = []
                st.session_state.current_barcodes = []
                st.session_state.selected_barcodes = set()
                st.rerun()
    
    # Mostrar vista previa si existe
    if st.session_state.current_barcodes:
        st.markdown("---")
        st.subheader("Vista Previa de Códigos")
        display_preview()
        
        # Botones de acción para etiquetas seleccionadas
        if st.session_state.selected_barcodes:
            st.markdown("---")
            st.subheader("Acciones con Seleccionadas")
            
            col_print, col_download = st.columns(2)
            
            with col_print:
                if st.button("🖨️ Imprimir Seleccionadas", key="print_selected_nexlab_btn", use_container_width=True):
                    print_selected_nexlab_barcodes(barcode_format)
            
            with col_download:
                st.write("")  # Espaciador para compatibilidad

if __name__ == "__main__":
    main()
