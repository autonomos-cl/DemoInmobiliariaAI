# Sistema de Análisis Inmobiliario con IA

Sistema que utiliza agentes de IA para análisis inmobiliario, integrando búsqueda web y almacenamiento en MongoDB.

## Requisitos

- Python 3.8+
- MongoDB Atlas cuenta
- OpenAI API key
- Serper API key

## Instalación

1. Clonar repositorio:
```bash
git clone [url-repositorio]
cd agenteinm
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno en `.env`:
```
OPENAI_API_KEY=tu_api_key_aqui
SERPER_API_KEY=tu_api_key_aqui
MONGODB_URI=tu_uri_mongodb_aqui
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## Estructura

```
agenteinm/
├── src/
│   └── agenteinm/
│       ├── config/
│       │   ├── agents.yaml    # Configuración de agentes
│       │   └── tasks.yaml     # Definición de tareas
│       ├── tools/
│       │   └── search_tool.py # Herramienta búsqueda web
│       ├── utils/
│       │   ├── db_manager.py  # Manejo MongoDB
│       │   └── check_reports.py # Verificación reportes
│       ├── crew.py           # Lógica principal
│       └── main.py           # Punto de entrada
└── reports/                  # Reportes generados
```

## Uso

1. Ejecutar análisis:
```bash
python src/agenteinm/main.py
```

2. Verificar reportes:
```bash
python src/agenteinm/utils/check_reports.py
```

## Agentes

- CEO Virtual: Análisis de mercado
- Abogado: Revisión legal
- Coordinador: Integración y supervisión

## Almacenamiento

- MongoDB Atlas: Almacenamiento principal
- Respaldo local: /reports/[fecha]/[tipo]_[timestamp].txt

# Google Drive Tools

Herramienta para gestionar archivos en Google Drive con funcionalidades de análisis y organización automática.

## Configuración Inicial

### 1. Configurar Credenciales de Google Drive

Si tienes las credenciales solo agrega el archivo al directerio raiz como credentials.json sino

para ingresar debes usar la cuenta agente@autonomos.dev y la contraseña


### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:
