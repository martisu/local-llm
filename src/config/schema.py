"""Configuration schema for Local LLM project."""

from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    name: str
    version: str
    description: str


class ServerConfig(BaseModel):
    host: str
    port: int
    debug: bool = False
    cors_origins: list[str] = []


class BackendConfig(BaseModel):
    type: str = "llama.cpp"
    base_url: str
    model: str
    context_length: int
    temperature: float
    max_tokens: int
    gpu_layers: int = -1
    threads: int = 4


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"
    file: str = "logs/app.log"


class FeaturesConfig(BaseModel):
    streaming: bool = True
    function_calling: bool = False
    system_prompt: bool = True
    chat_template: bool = True


class AppConfig(BaseModel):
    project: ProjectConfig
    server: ServerConfig
    backend: BackendConfig
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
