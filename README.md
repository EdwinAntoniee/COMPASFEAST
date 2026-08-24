# Maintain

Maintain combines Predictive AI, using Scikit-Learn and LightGBM, with Generative AI, using a local large language model served by Ollama. It detects industrial machine failure modes from sensor readings and provides repair guidance through a FastAPI web application.

## Prerequisites

Install the following on the host machine:

- Docker
- Docker Compose
- Ollama

The application expects Ollama on port `11434`. Docker Compose connects to the host Ollama instance through `host.docker.internal`.


## Important Model Setup

The LLM model is too large for GitHub. Download the `.gguf` model and its `Modelfile` from:

https://drive.google.com/file/d/1LzGVKWS1hSP6TNHwD9AYldaVgjhWCjxp/view?usp=sharing

Place both downloaded files exactly inside:

```text
BackEnd/models/qwen-sop-model_gguf/
```

The directory should contain both `Modelfile` and the `.gguf` model file. Open a terminal in that directory and run:

```bash
ollama create qwen-model -f Modelfile
```

Verify that `qwen-model` is available:

```bash
ollama list
```

## How to Run

1. Start Ollama on the host machine:

	```bash
	ollama serve
	```

	If Ollama is already running as a system service, leave it running and do not start a second server.

2. Confirm that `qwen-model` is installed:

	```bash
	ollama list
	```

3. From the repository root, build and start the application:

	```bash
	docker-compose up --build
	```

4. Open the web interface at [http://localhost:8000](http://localhost:8000).

FastAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

Stop the application with:

```bash
docker-compose down
```

## Project Structure

```text
.
├── BackEnd/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── Dockerfile
│   ├── main.py
│   
├── FrontEnd/
├── requirements.txt
├── docker-compose.yml
└── README.md
```
