"""Main application entry point for Local LLM project."""

from config import load_config, get_backend_url, get_model_name


def main():
    config = load_config()

    print(f"Project: {config.project.name} v{config.project.version}")
    print(f"Server: {config.server.host}:{config.server.port}")
    print()
    print(f"Backend: {config.backend.type}")
    print(f"Model: {config.backend.model}")
    print(f"URL: {config.backend.base_url}")
    print(f"Context: {config.backend.context_length}")
    print(f"Temperature: {config.backend.temperature}")


if __name__ == "__main__":
    main()
