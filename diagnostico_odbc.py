"""
Script de diagnóstico para verificar drivers ODBC instalados
Ejecutar: python diagnostico_odbc.py
"""
import pyodbc

print("=" * 60)
print("DIAGNÓSTICO DE DRIVERS ODBC")
print("=" * 60)
print()

try:
    drivers = pyodbc.drivers()
    
    if drivers:
        print(f"✅ Se encontraron {len(drivers)} driver(s) ODBC instalado(s):")
        print()
        
        sql_server_drivers = []
        other_drivers = []
        
        for driver in drivers:
            if 'SQL Server' in driver:
                sql_server_drivers.append(driver)
            else:
                other_drivers.append(driver)
        
        if sql_server_drivers:
            print("🔵 DRIVERS DE SQL SERVER:")
            for driver in sql_server_drivers:
                print(f"   ✓ {driver}")
            print()
        else:
            print("❌ NO SE ENCONTRARON DRIVERS DE SQL SERVER")
            print()
        
        if other_drivers:
            print("🔹 OTROS DRIVERS:")
            for driver in other_drivers:
                print(f"   • {driver}")
            print()
    else:
        print("❌ NO SE ENCONTRARON DRIVERS ODBC INSTALADOS")
        print()
    
    print("=" * 60)
    print("RECOMENDACIONES:")
    print("=" * 60)
    
    if not sql_server_drivers:
        print()
        print("⚠️  Necesitas instalar un driver ODBC para SQL Server")
        print()
        print("Opciones de descarga:")
        print("1. ODBC Driver 18 for SQL Server (Recomendado)")
        print("   https://go.microsoft.com/fwlink/?linkid=2223304")
        print()
        print("2. ODBC Driver 17 for SQL Server")
        print("   https://go.microsoft.com/fwlink/?linkid=2187214")
        print()
        print("3. Documentación completa:")
        print("   https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        print()
    else:
        print()
        print("✅ Tienes drivers de SQL Server instalados")
        print(f"✅ Se usará: {sql_server_drivers[0]}")
        print()
        print("La aplicación debería funcionar correctamente.")
        print("Si aún tienes problemas, verifica:")
        print("  • Servidor SQL Server está activo")
        print("  • Credenciales son correctas")
        print("  • Firewall permite la conexión")
        print()
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print()
    print("Asegúrate de tener instalado pyodbc:")
    print("  pip install pyodbc")

print("=" * 60)
