# Sistema de agentes inmobiliarios usando CrewAI
# Integra CEO Virtual, Abogado y Coordinador para análisis inmobiliario
# Usa MongoDB Atlas para almacenamiento y Serper para búsquedas web

from crewai import Agent, Crew, Process, Task
from datetime import datetime
import os
import yaml
from langchain.tools import Tool
from tools.search_tool import SerperSearchTool
from utils.db_manager import DatabaseManager

class Agenteinm:
    def __init__(self):
        # Inicializa configuraciones y herramientas
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.agents_config = os.path.join(self.base_dir, 'config', 'agents.yaml')
        self.tasks_config = os.path.join(self.base_dir, 'config', 'tasks.yaml')
        
        # Herramienta de búsqueda web
        self.search_tool = SerperSearchTool()
        self.tools = [Tool(name="Internet Search", func=self.search_tool._run, description=self.search_tool.description)]
        
        # Conexión a MongoDB Atlas
        self.db_manager = DatabaseManager()

    def _save_report(self, task_output, report_type: str, metadata: dict = None) -> str:
        # Guarda reportes en MongoDB y localmente
        try:
            content = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
            metadata = metadata or {}
            if hasattr(task_output, 'agent'): metadata['agent'] = task_output.agent
            
            report_id = self.db_manager.save_report(report_type=report_type, content=content, metadata=metadata)
            self._save_local_report(content, report_type)
            return content
        except Exception as e:
            print(f"❌ Error MongoDB: {str(e)}")
            self._save_local_report(str(task_output), report_type)
            return str(task_output)

    def _save_local_report(self, content: str, base_filename: str):
        # Backup local de reportes
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = f"reports/{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(reports_dir, exist_ok=True)
        filepath = f"{reports_dir}/{base_filename}_{timestamp}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _load_config(self, config_path: str) -> dict:
        # Carga configuraciones YAML
        with open(config_path, encoding='utf-8') as f:
            return yaml.safe_load(f)

    # Definición de agentes
    def task_manager(self) -> Agent:
        # Coordinador principal
        config = self._load_config(self.agents_config)['task_manager']
        return Agent(role=config['role'], goal=config['goal'], backstory=config['backstory'],
                    verbose=True, allow_delegation=True, tools=self.tools,
                    llm_config=config.get('llm_config', {}))

    def ceo_virtual(self) -> Agent:
        # Análisis de mercado
        config = self._load_config(self.agents_config)['ceo_virtual']
        return Agent(role=config['role'], goal=config['goal'], backstory=config['backstory'],
                    verbose=True, allow_delegation=False, tools=self.tools,
                    llm_config=config.get('llm_config', {}))

    def legal_assistant(self) -> Agent:
        # Análisis legal
        config = self._load_config(self.agents_config)['legal_assistant']
        return Agent(role=config['role'], goal=config['goal'], backstory=config['backstory'],
                    verbose=True, allow_delegation=False, tools=self.tools,
                    llm_config=config.get('llm_config', {}))

    # Definición de tareas
    def market_analysis_task(self) -> Task:
        # Análisis de mercado inmobiliario
        config = self._load_config(self.tasks_config)['market_analysis_task']
        return Task(description=config['description'], expected_output=config['expected_output'],
                   agent=self.ceo_virtual(),
                   callback=lambda task_output: self._save_report(task_output, 'market_analysis',
                                                                {'agent': 'ceo_virtual'}))

    def legal_review_task(self) -> Task:
        # Revisión legal
        config = self._load_config(self.tasks_config)['legal_review_task']
        return Task(description=config['description'], expected_output=config['expected_output'],
                   agent=self.legal_assistant(),
                   callback=lambda task_output: self._save_report(task_output, 'legal_review',
                                                                {'agent': 'legal_assistant'}))

    def coordination_task(self) -> Task:
        # Coordinación general
        config = self._load_config(self.tasks_config)['coordination_task']
        return Task(description=config['description'], expected_output=config['expected_output'],
                   agent=self.task_manager(),
                   callback=lambda task_output: self._save_report(task_output, 'coordination_report',
                                                                {'agent': 'task_manager'}))

    def crew(self) -> Crew:
        # Configura el equipo y flujo de trabajo
        return Crew(
            agents=[self.task_manager(), self.ceo_virtual(), self.legal_assistant()],
            tasks=[self.market_analysis_task(), self.legal_review_task(), self.coordination_task()],
            process=Process.sequential,
            verbose=True
        )

    def __del__(self):
        # Limpieza de conexiones
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
