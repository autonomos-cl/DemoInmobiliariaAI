from crewai import Agent, Crew, Process, Task
from datetime import datetime
import os
import yaml
from langchain.tools import Tool
from tools.search_tool import SerperSearchTool

class Agenteinm:
    """Agenteinm crew con estructura jerárquica liderada por Task Manager"""

    def __init__(self):
        # Get the directory where this script is located
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.agents_config = os.path.join(self.base_dir, 'config', 'agents.yaml')
        self.tasks_config = os.path.join(self.base_dir, 'config', 'tasks.yaml')
        print(f"Loading configs from:\nAgents: {self.agents_config}\nTasks: {self.tasks_config}")
        
        # Initialize tools
        self.search_tool = SerperSearchTool()
        self.tools = [
            Tool(
                name="Internet Search",
                func=self.search_tool._run,
                description=self.search_tool.description
            )
        ]

    def _get_output_path(self, base_filename: str) -> str:
        """Helper para generar rutas de archivo con timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = f"reports/{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(reports_dir, exist_ok=True)
        return f"{reports_dir}/{base_filename}_{timestamp}.txt"

    def _load_config(self, config_path: str) -> dict:
        """Helper para cargar configuración desde archivo YAML"""
        try:
            with open(config_path, encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config from {config_path}: {str(e)}")
            raise

    def task_manager(self) -> Agent:
        """Task Manager que coordina el equipo inmobiliario"""
        config = self._load_config(self.agents_config)['task_manager']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm_config=config.get('llm_config', {})
        )

    def ceo_virtual(self) -> Agent:
        """CEO Virtual especializado en análisis de mercado"""
        config = self._load_config(self.agents_config)['ceo_virtual']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm_config=config.get('llm_config', {})
        )

    def legal_assistant(self) -> Agent:
        """Asistente Legal especializado en análisis jurídico"""
        config = self._load_config(self.agents_config)['legal_assistant']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm_config=config.get('llm_config', {})
        )

    def market_analysis_task(self) -> Task:
        """Tarea de análisis de mercado"""
        config = self._load_config(self.tasks_config)['market_analysis_task']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.ceo_virtual()
        )

    def legal_review_task(self) -> Task:
        """Tarea de revisión legal"""
        config = self._load_config(self.tasks_config)['legal_review_task']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.legal_assistant()
        )

    def coordination_task(self) -> Task:
        """Tarea principal de coordinación"""
        config = self._load_config(self.tasks_config)['coordination_task']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.task_manager()
        )

    def crew(self) -> Crew:
        """Crea el crew inmobiliario con estructura jerárquica"""
        return Crew(
            agents=[
                self.task_manager(),
                self.ceo_virtual(),
                self.legal_assistant()
            ],
            tasks=[
                self.market_analysis_task(),
                self.legal_review_task(),
                self.coordination_task()
            ],
            process=Process.sequential,
            verbose=True
        )
