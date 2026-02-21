from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass(frozen=True)
class SecurityConfig:
    jwt_secret: str
    flask_secret: str
    environment: str


def _require_env(name: str, min_length: int) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(
            f"❌ CRITICAL ERROR: {name} environment variable is required!\n"
            f"Set {name} with a strong, random secret (min {min_length} characters)"
        )
    if len(value) < min_length:
        raise ValueError(
            f"❌ CRITICAL ERROR: {name} must be at least {min_length} characters long!\n"
            f"Current length: {len(value)} characters"
        )
    return value


def load_security_config() -> SecurityConfig:
    load_dotenv()
    environment = os.getenv("ENVIRONMENT") or os.getenv("FLASK_ENV", "development")
    environment = environment.lower()
    return SecurityConfig(
        jwt_secret=_require_env("JWT_SECRET", 32),
        flask_secret=_require_env("FLASK_SECRET_KEY", 32),
        environment=environment,
    )


def get_allowed_origins() -> list[str]:
    configured = os.getenv("CORS_ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS", "")
    configured = configured.strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:8082",
        "http://127.0.0.1:8082",
        "http://localhost:8083",
        "http://127.0.0.1:8083",
        "http://172.20.10.10:8080",
        "http://192.168.56.1:8080",
        "http://172.24.144.1:8080",

    ]


def get_rate_limits() -> list[str]:
    configured = os.getenv("RATE_LIMITS", "").strip()
    if configured:
        return [limit.strip() for limit in configured.split(",") if limit.strip()]
    return ["200 per day", "50 per hour"]
