# Generador de Códigos de Barras - Versión Web con Streamlit

Esta es la versión web de la aplicación de generación de códigos de barras para impresoras Zebra, desarrollada con Streamlit.

## 🚀 Características

- ✅ **Ingreso Manual**: Ingresa datos individuales (Orden GRAU y Nombres)
- ✅ **Modo Excel**: Importa datos desde archivos Excel
- ✅ **Búsqueda por Orden (Nexlab)**: Busca órdenes en base de datos SQL Server
- ✅ **Múltiples formatos**: CODE128, CODE39, EAN13, EAN8, UPC-A, ITF
- ✅ **Vista previa**: Visualiza códigos antes de imprimir
- ✅ **Impresión directa**: Conecta con impresoras Zebra
- ✅ **Descarga ZIP**: Descarga todos los códigos como imágenes
- ✅ **Filtros avanzados**: Filtra y selecciona códigos específicos
- ✅ **Interfaz moderna**: UI responsiva y fácil de usar
- ✅ **Impresión doble**: Opción para imprimir cada etiqueta 2 veces

## 📋 Requisitos

- Python 3.8 o superior
- Windows (para conexión con impresoras Zebra)
- Impresora Zebra instalada y configurada

## 🔧 Instalación

1. Navega a la carpeta web_app:
```bash
cd web_app
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

Ejecuta la aplicación con:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📖 Uso

### Búsqueda por Orden (Nexlab) - NUEVO 🆕

1. Selecciona "🔍 Búsqueda por Orden (Nexlab)" en la parte superior
2. **Primera vez**: Configura la conexión a la base de datos
   - Edita el archivo `modules/ordenes_nexlab.py`
   - Configura: servidor, base de datos, usuario y contraseña
   - Ver documentación completa en [CONFIGURACION_NEXLAB.md](CONFIGURACION_NEXLAB.md)
3. Prueba la conexión haciendo clic en "🔌 Probar Conexión a Base de Datos"
4. Ingresa el **Número de Orden** (ej: 1622485)
5. Haz clic en **"🔍 Buscar"**
6. Revisa los datos del paciente mostrados
7. Selecciona el número de copias (1-10)
8. Haz clic en **"🖨️ Imprimir Etiqueta"** o **"📥 Descargar Imagen"**

**Características:**
- Búsqueda automática en base de datos SQL Server
- Generación automática de etiquetas con formato: `NúmeroOrden.01`
- Visualización de datos del paciente (Nombre completo, Sexo, Estado)
- Ver órdenes recientes (últimas 20 órdenes)
- Impresión múltiple (1-10 copias)

### Ingreso Manual

1. Selecciona "📝 Ingreso Manual" en la parte superior
2. Ingresa el **Número de Orden (GRAU)**
3. Ingresa los **Apellidos y Nombres**
4. Haz clic en **"➕ Agregar a la lista"**
5. Repite los pasos 2-4 para agregar más etiquetas
6. Haz clic en **"🔍 Vista Previa"** para generar los códigos
7. Selecciona las etiquetas que deseas imprimir (0 = No, 1 = Sí)
8. Haz clic en **"🖨️ Imprimir Seleccionadas"**

**Características del Ingreso Manual:**
- Agrega múltiples entradas a una lista
- Elimina entradas individuales con el botón 🗑️
- Limpia toda la lista con "🗑️ Limpiar Lista"
- El formato del código se configura en el sidebar (ej: `{}.01`)

### Modo Manual

1. Selecciona "📝 Manual (Rango)" en el sidebar
2. Configura el formato de código de barras
3. Ingresa el formato de número (ej: `{}.01`)
4. Define el rango DESDE-HASTA
5. Opciones:
   - **Vista Previa**: Genera y muestra los códigos
   - **Imprimir**: Envía directamente a la impresora
   - **Descargar ZIP**: Descarga todos como imágenes PNG

### Modo Excel

1. Selecciona "📑 Desde Excel" en el sidebar
2. Sube tu archivo Excel (.xlsx o .xls)
3. Selecciona las columnas:
   - Columna de Nombres
   - Columna de Solicitud
   - Columna de Grau (opcional)
4. Vista previa de los datos
5. Selecciona registros:
   - **Todos**: Selecciona todos los registros
   - **Rango**: Define un rango de filas
   - **Manual**: Ingresa filas específicas (ej: `1,3,5-10`)
6. Genera, imprime o descarga

## 🎨 Características Adicionales

### Filtros de Vista Previa
- Filtra códigos generados usando rangos (ej: `1-5, 8, 10-15`)
- Visualiza solo los códigos que necesitas

### Formato Personalizado
- `{}` = Número simple (1, 2, 3...)
- `{}.01` = Número con sufijo (1.01, 2.01, 3.01...)
- Cualquier formato personalizado con `{}`

### Configuración de Impresora
- Detecta automáticamente impresoras Zebra
- Actualiza la lista de impresoras disponibles
- Compatible con impresoras locales y de red

## 📁 Estructura del Proyecto

```
web_app/
├── app.py                    # Aplicación principal Streamlit
├── requirements.txt          # Dependencias
├── README.md                 # Esta documentación
├── CONFIGURACION_NEXLAB.md   # Guía de configuración del módulo Nexlab
├── modules/                  # Módulos de la aplicación
│   ├── __init__.py
│   ├── barcode_web.py        # Generador de códigos
│   ├── zebra_web.py          # Conexión con impresoras
│   ├── excel_web.py          # Lector de Excel
│   └── ordenes_nexlab.py     # Búsqueda en base de datos SQL Server (NUEVO)
├── assets/                   # Recursos estáticos
└── temp/                     # Archivos temporales
```

## 🔍 Diferencias con la Versión de Escritorio

### Ventajas de la Versión Web:
- ✅ Interfaz más moderna y responsiva
- ✅ Accesible desde cualquier navegador
- ✅ Fácil de compartir (puede ejecutarse en servidor)
- ✅ Descarga de códigos en ZIP
- ✅ Vista previa mejorada con grid
- ✅ Filtros más avanzados

### Mantenido de la Versión Original:
- ✅ Todas las funcionalidades principales
- ✅ Conexión con impresoras Zebra
- ✅ Soporte de múltiples formatos
- ✅ Lectura de Excel
- ✅ Generación de códigos ZPL

## 🛠️ Solución de Problemas

### No se detectan impresoras
- Verifica que la impresora Zebra esté instalada y encendida
- Haz clic en "🔄 Actualizar Impresoras"
- Verifica los drivers de la impresora

### Error al cargar Excel
- Verifica que el archivo sea .xlsx o .xls válido
- Asegúrate de que el archivo no esté protegido
- Verifica que las columnas tengan datos

### Códigos no se imprimen
- Verifica la conexión con la impresora
- Revisa que la impresora esté configurada correctamente
- Prueba con un código de prueba primero

### Problemas con Base de Datos (Nexlab)
- Verifica que SQL Server esté activo
- Asegúrate de tener instalado "ODBC Driver 17 for SQL Server" o superior
- Revisa las credenciales en `modules/ordenes_nexlab.py`
- Verifica que el usuario tenga permisos de lectura en las tablas
- Ver [CONFIGURACION_NEXLAB.md](CONFIGURACION_NEXLAB.md) para más detalles

## 📝 Notas

- Esta es una versión **completamente separada** de la aplicación de escritorio
- Ambas versiones pueden coexistir sin problemas
- Los módulos están adaptados específicamente para Streamlit
- No afecta ni modifica la aplicación original en tkinter

## 🎯 Próximas Mejoras

- [ ] Modo oscuro/claro
- [ ] Exportar a PDF
- [ ] Plantillas predefinidas
- [ ] Historial de generaciones
- [ ] Configuración de etiqueta personalizada
- [ ] Soporte para más formatos de código

## 📧 Soporte

Para problemas o sugerencias, consulta la documentación principal del proyecto.

---

**Versión Web**: 1.0.0  
**Desarrollado con**: Streamlit + Python  
**Compatible con**: Windows 10/11
