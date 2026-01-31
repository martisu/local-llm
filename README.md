# Local LLM

Local llama.cpp inference server with centralized configuration.

## Quick Start

```bash
# Copy environment configuration
cp .env.example .env

# Edit .env to set your model
# LLAMA_MODEL=Qwen3-4B-Instruct-2507-GGUF

# Run the application
source venv/bin/activate
python src/main.py
```

## Configuration

All settings are managed via `config.yaml` and `.env`:

- **Model**: Edit `LLAMA_MODEL` in `.env`
- **Server**: Change `SERVER_PORT` in `.env`
- **Inference**: Tune `temperature`, `context_length`, `max_tokens` in `.env`

## Project Structure

```
.
├── config.yaml          # Main configuration (Jinja2-templated)
├── .env.example         # Environment template
├── .env                 # Your local settings (gitignored)
├── src/
│   ├── config/          # Configuration loader & schema
│   │   ├── schema.py    # Pydantic validation models
│   │   └── loader.py    # YAML + Jinja2 + env var loading
│   └── main.py          # Application entry point
├── inference/           # Model files & inference setup
│   └── llama/
└── venv/                # Python virtual environment
```

## Switching Models

Edit `.env`:

```bash
LLAMA_MODEL=your-model-name.gguf
```

Then restart the application.

## Requirements

- Python 3.11+
- llama.cpp server running on port 11434
