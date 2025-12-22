"""
Script de prueba para verificar que todos los módulos funcionan correctamente
"""
import sys
import os

# Agregar paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_imports():
    """Prueba que todos los módulos se puedan importar"""
    print("🔍 Probando importaciones...")
    
    try:
        from modules.barcode_web import BarcodeWebGenerator
        print("  ✅ BarcodeWebGenerator importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando BarcodeWebGenerator: {e}")
        return False
    
    try:
        from modules.zebra_web import ZebraWebPrinter
        print("  ✅ ZebraWebPrinter importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando ZebraWebPrinter: {e}")
        return False
    
    try:
        from modules.excel_web import ExcelWebReader
        print("  ✅ ExcelWebReader importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando ExcelWebReader: {e}")
        return False
    
    return True

def test_barcode_generation():
    """Prueba la generación de códigos de barras"""
    print("\n📊 Probando generación de códigos de barras...")
    
    try:
        from modules.barcode_web import BarcodeWebGenerator
        
        generator = BarcodeWebGenerator()
        
        # Probar formatos soportados
        formats = generator.get_supported_formats()
        print(f"  ℹ️  Formatos soportados: {', '.join(formats)}")
        
        # Generar código de prueba
        img = generator.generate_barcode('CODE128', '123456')
        print(f"  ✅ Código de barras generado: {img.size[0]}x{img.size[1]} px")
        
        # Probar con texto adicional
        img_with_text = generator.generate_barcode_with_text(
            'CODE128', 
            '123456', 
            'Nombre de Prueba',
            'A+'
        )
        print(f"  ✅ Código con texto generado: {img_with_text.size[0]}x{img_with_text.size[1]} px")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en generación de códigos: {e}")
        return False

def test_printer_detection():
    """Prueba la detección de impresoras"""
    print("\n🖨️  Probando detección de impresoras...")
    
    try:
        from modules.zebra_web import ZebraWebPrinter
        
        printer = ZebraWebPrinter()
        printers = printer.get_available_printers()
        
        if printers:
            print(f"  ✅ Impresoras encontradas: {len(printers)}")
            for p in printers:
                print(f"     - {p}")
        else:
            print("  ⚠️  No se encontraron impresoras")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error detectando impresoras: {e}")
        return False

def test_dependencies():
    """Prueba que todas las dependencias estén instaladas"""
    print("\n📦 Verificando dependencias...")
    
    dependencies = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'openpyxl': 'OpenPyXL',
        'barcode': 'python-barcode',
        'PIL': 'Pillow',
        'win32print': 'pywin32'
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {name} instalado")
        except ImportError:
            print(f"  ❌ {name} NO instalado")
            all_ok = False
    
    return all_ok

def main():
    """Función principal de pruebas"""
    print("=" * 60)
    print("  PRUEBAS DE MÓDULOS - Aplicación Web Streamlit")
    print("=" * 60)
    
    results = []
    
    # Probar dependencias
    results.append(("Dependencias", test_dependencies()))
    
    # Probar importaciones
    results.append(("Importaciones", test_imports()))
    
    # Probar generación de códigos
    results.append(("Generación de Códigos", test_barcode_generation()))
    
    # Probar detección de impresoras
    results.append(("Detección de Impresoras", test_printer_detection()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status:12} - {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Pruebas pasadas: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! La aplicación está lista.")
        print("\n▶️  Para ejecutar la aplicación:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("\n💡 Soluciones:")
        print("   1. Instala dependencias: pip install -r requirements.txt")
        print("   2. Verifica que Python 3.8+ esté instalado")
        print("   3. En Windows, verifica drivers de impresora Zebra")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
