#!/usr/bin/env python
import sys
import warnings
from datetime import datetime

from agenteinm.crew import Agenteinm

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Ejecuta el crew inmobiliario con estructura jerárquica.
    El Task Manager coordina el análisis integral del mercado inmobiliario.
    """
    inputs = {
        'zona': 'Santiago Centro',
        'fecha': datetime.now().strftime("%Y-%m-%d"),
        'tipo_propiedad': 'Residencial',
        'presupuesto_min': '1000 UF',
        'presupuesto_max': '5000 UF'
    }
    
    print("\nIniciando análisis inmobiliario...")
    print(f"Zona: {inputs['zona']}")
    print(f"Fecha: {inputs['fecha']}")
    print(f"Tipo de Propiedad: {inputs['tipo_propiedad']}")
    print(f"Rango de Presupuesto: {inputs['presupuesto_min']} - {inputs['presupuesto_max']}\n")
    
    crew = Agenteinm().crew()
    results = crew.kickoff(inputs=inputs)
    
    reports_dir = f"reports/{datetime.now().strftime('%Y-%m-%d')}"
    print("\nAnálisis completado!")
    print(f"Reportes generados en: {reports_dir}/")
    print("- market_analysis_[timestamp].md: Análisis de mercado del CEO Virtual")
    print("- legal_review_[timestamp].md: Análisis legal del Abogado")
    print("- coordination_report_[timestamp].md: Reporte integrado del Task Manager")
    
    return results

def train():
    """
    Entrena el crew para mejorar la coordinación y respuestas.
    """
    inputs = {
        'zona': 'Santiago Centro',
        'fecha': datetime.now().strftime("%Y-%m-%d"),
        'tipo_propiedad': 'Residencial',
        'presupuesto_min': '1000 UF',
        'presupuesto_max': '5000 UF'
    }
    try:
        Agenteinm().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"Error durante el entrenamiento: {e}")

def replay():
    """
    Reproduce una ejecución específica del crew.
    """
    try:
        Agenteinm().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"Error durante la reproducción: {e}")

def test():
    """
    Prueba el crew con diferentes configuraciones.
    """
    inputs = {
        'zona': 'Santiago Centro',
        'fecha': datetime.now().strftime("%Y-%m-%d"),
        'tipo_propiedad': 'Residencial',
        'presupuesto_min': '1000 UF',
        'presupuesto_max': '5000 UF'
    }
    try:
        Agenteinm().crew().test(
            n_iterations=int(sys.argv[1]),
            openai_model_name=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"Error durante las pruebas: {e}")

if __name__ == "__main__":
    run()
