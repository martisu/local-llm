# Local LLM Project

## Overview

Python project for running local llama.cpp inference server with centralized configuration management.

## Key Files

- `config.yaml` - Main configuration (Jinja2-templated)
- `.env` - Environment variables (gitignored)
- `src/config/loader.py` - Loads config with env var substitution
- `src/config/schema.py` - Pydantic validation models

## Configuration Flow

1. `config.yaml` uses `${VAR:default}` syntax for env vars
2. `loader.py` renders Jinja2 templates and substitutes env vars
3. `schema.py` validates the final config with Pydantic

## Docker Services

**macOS (Apple Silicon)**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.macos.yml up -d --build
```

**Linux**:
```bash
docker-compose up -d
```

## Common Tasks

### Run the application
```bash
source venv/bin/activate && python src/main.py
```

### Change model
Edit `LLAMA_MODEL` in `.env` file.

### Rebuild Docker container
```bash
docker-compose -f docker-compose.yml -f docker-compose.macos.yml up -d --build
```

## Environment Variables

Key variables in `.env`:
- `LLAMA_MODEL` - Model filename in `llama/models/`
- `SERVER_PORT` - Application server port (default: 8000)
- `LLAMA_PORT` - llama.cpp server port (default: 11434)
