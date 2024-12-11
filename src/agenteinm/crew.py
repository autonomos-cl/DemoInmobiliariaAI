from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from datetime import datetime
import os

@CrewBase
class Agenteinm():
    """Agenteinm crew con estructura jerárquica liderada por Task Manager"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def _get_output_path(self, base_filename: str) -> str:
        """Helper para generar rutas de archivo con timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = f"reports/{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(reports_dir, exist_ok=True)
        return f"{reports_dir}/{base_filename}_{timestamp}.md"

    @agent
    def task_manager(self) -> Agent:
        """Task Manager que coordina el equipo inmobiliario"""
        return Agent(
            role="Coordinador de Operaciones Inmobiliarias",
            goal="Coordinar eficientemente el equipo inmobiliario, asegurando respuestas integradas y resultados rápidos",
            backstory="Experto en gestión de equipos inmobiliarios con amplia experiencia en coordinación de agentes y optimización de procesos.",
            verbose=True,
            allow_delegation=True,
            is_manager=True
        )

    @agent
    def ceo_virtual(self) -> Agent:
        """CEO Virtual especializado en análisis de mercado"""
        return Agent(
            config=self.agents_config['ceo_virtual'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def legal_assistant(self) -> Agent:
        """Asistente Legal especializado en análisis jurídico"""
        return Agent(
            config=self.agents_config['legal_assistant'],
            verbose=True,
            allow_delegation=False
        )

    @task
    def market_analysis_task(self) -> Task:
        """Tarea de análisis de mercado"""
        return Task(
            config=self.tasks_config['market_analysis_task'],
            agent=self.ceo_virtual(),
            output_file=self._get_output_path('market_analysis')
        )

    @task
    def legal_review_task(self) -> Task:
        """Tarea de revisión legal"""
        return Task(
            config=self.tasks_config['legal_review_task'],
            agent=self.legal_assistant(),
            output_file=self._get_output_path('legal_review')
        )

    @task
    def coordination_task(self) -> Task:
        """Tarea principal de coordinación"""
        return Task(
            config=self.tasks_config['coordination_task'],
            agent=self.task_manager(),
            output_file=self._get_output_path('coordination_report')
        )

    @crew
    def crew(self) -> Crew:
        """Crea el crew inmobiliario con estructura jerárquica"""
        return Crew(
            agents=[self.ceo_virtual(), self.legal_assistant()],
            tasks=[
                self.market_analysis_task(),
                self.legal_review_task(),
                self.coordination_task()
            ],
            process=Process.sequential,  # Cambiado a sequential para asegurar el orden correcto
            manager_agent=self.task_manager(),
            verbose=True
        )
