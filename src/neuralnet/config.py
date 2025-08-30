"""Configuration management for Back of the Neural Net."""

import os
from typing import Optional
from pydantic import BaseModel, Field

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, continue without it
    pass


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    
    # Provider type: "mock", "lmstudio", or "openai"
    provider: str = Field(default="mock", description="LLM provider type")
    
    # LM Studio specific settings
    lmstudio_base_url: str = Field(default="http://localhost:1234/v1", description="LM Studio API base URL")
    lmstudio_model: Optional[str] = Field(default=None, description="Model name in LM Studio")
    
    # OpenAI settings (for future use)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model name")
    
    # General LLM settings
    temperature: float = Field(default=0.7, description="LLM temperature for creativity")
    max_tokens: int = Field(default=1000, description="Maximum tokens per response")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class Config(BaseModel):
    """Main application configuration."""
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    
    # Server settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Game settings
    use_tools: bool = Field(default=True, description="Enable game state tools for LLM")


def load_config() -> Config:
    """Load configuration from environment variables."""
    config = Config()
    
    # Load LLM configuration from environment
    config.llm.provider = os.getenv("LLM_PROVIDER", "mock")
    config.llm.lmstudio_base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    config.llm.lmstudio_model = os.getenv("LMSTUDIO_MODEL")
    config.llm.openai_api_key = os.getenv("OPENAI_API_KEY")
    config.llm.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Parse numeric values with defaults
    try:
        config.llm.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    except ValueError:
        config.llm.temperature = 0.7
        
    try:
        config.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    except ValueError:
        config.llm.max_tokens = 1000
        
    try:
        config.llm.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
    except ValueError:
        config.llm.timeout = 30
    
    # Load server configuration
    config.host = os.getenv("SERVER_HOST", "127.0.0.1")
    try:
        config.port = int(os.getenv("SERVER_PORT", "8000"))
    except ValueError:
        config.port = 8000
    
    # Load game settings
    config.use_tools = os.getenv("USE_TOOLS", "true").lower() in ("true", "1", "yes")
    
    return config


def validate_llm_config(config: Config) -> None:
    """Validate LLM configuration and raise an error if invalid."""
    if config.llm.provider == "lmstudio":
        if not config.llm.lmstudio_model:
            raise ValueError(
                "LM Studio model must be specified when using lmstudio provider. "
                "Set LMSTUDIO_MODEL environment variable or configure it in your setup."
            )
    elif config.llm.provider == "openai":
        if not config.llm.openai_api_key:
            raise ValueError(
                "OpenAI API key must be specified when using openai provider. "
                "Set OPENAI_API_KEY environment variable."
            )
    elif config.llm.provider not in ("mock", "lmstudio", "openai"):
        raise ValueError(
            f"Unknown LLM provider: {config.llm.provider}. "
            "Supported providers: mock, lmstudio, openai"
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None