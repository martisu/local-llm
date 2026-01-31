# Local LLM

Local llama.cpp inference server with centralized configuration.

## Quick Start

```bash
# 1. Copy environment configuration
cp .env.example .env

# 2. Start llama.cpp server (macOS ARM64)
docker-compose -f docker-compose.yml -f docker-compose.macos.yml up -d --build

# 3. Run the application
source venv/bin/activate
python src/main.py
```

## Docker Compose

### macOS (Apple Silicon)

```bash
# Build and start
docker-compose -f docker-compose.yml -f docker-compose.macos.yml up -d --build

# View logs
docker-compose -f docker-compose.yml -f docker-compose.macos.yml logs -f

# Stop
docker-compose -f docker-compose.yml -f docker-compose.macos.yml down
```

### Linux

```bash
# Use base config only
docker-compose up -d

# Or with custom settings
docker-compose -f docker-compose.yml up -d
```

## Configuration

All settings are managed via `config.yaml` and `.env`:

- **Model**: Edit `LLAMA_MODEL` in `.env`
- **Server**: Change `SERVER_PORT` in `.env`
- **Inference**: Tune `temperature`, `context_length`, `max_tokens` in `.env`

## Project Structure

```
.
├── config.yaml              # Main configuration (Jinja2-templated)
├── .env.example             # Environment template
├── .env                     # Your local settings (gitignored)
├── docker-compose.yml       # Base Docker Compose config
├── docker-compose.macos.yml # macOS ARM64 override
├── src/
│   ├── config/              # Configuration loader & schema
│   │   ├── schema.py        # Pydantic validation models
│   │   └── loader.py        # YAML + Jinja2 + env var loading
│   └── main.py              # Application entry point
├── llama/                   # llama.cpp setup
│   ├── Dockerfile           # ARM64 build for Apple Silicon
│   └── models/              # Model files (.gguf)
└── venv/                    # Python virtual environment
```

## Switching Models

Edit `.env`:

```bash
LLAMA_MODEL=your-model-name.gguf
```

Then restart the application.

## Requirements

- Python 3.11+
- Docker & Docker Compose
- llama.cpp server (started via docker-compose)
