# Script para verificar reportes guardados en MongoDB Atlas
# Muestra ID, fecha y agente para cada tipo de reporte
# Útil para validar que los reportes se guardaron correctamente

from db_manager import DatabaseManager

def main():
    try:
        # Conecta a MongoDB
        db = DatabaseManager()
        print("✅ Conexión exitosa a MongoDB Atlas")

        # Verifica reportes por tipo
        tipos_reporte = ['market_analysis', 'legal_review', 'coordination_report']
        for tipo in tipos_reporte:
            reports = db.get_reports_by_type(tipo)
            print(f"\nReportes de tipo {tipo}:")
            for report in reports:
                print(f"ID: {report['_id']}")
                print(f"Fecha: {report['created_at']}")
                print(f"Agente: {report['metadata'].get('agent', 'No especificado')}")
                print("-" * 50)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    main()
