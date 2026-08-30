from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """
    AI Processing Engine Settings.
    Loads values from environment variables or .env file.
    """
    SOURCE_TYPE: str = Field(default="WEBCAM", description="Camera source type: WEBCAM or VIDEO_FILE")
    CAMERA_INDEX: int = Field(default=0, description="Device index for webcam ingestion (e.g. 0, 1)")
    VIDEO_PATH: Optional[str] = Field(default=None, description="Path to local video file for VIDEO_FILE mode")
    FRAME_WIDTH: Optional[int] = Field(default=None, description="Target width for frame processing/display")
    FRAME_HEIGHT: Optional[int] = Field(default=None, description="Target height for frame processing/display")
    DISPLAY_PREVIEW: bool = Field(default=True, description="Enable GUI window live preview with overlays")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    MODEL_SHA256: Optional[str] = Field(default=None, description="Expected SHA-256 digest of YOLO weights (optional verification)")

    # M1 Backend Integration Settings

    BACKEND_URL: str = Field(default="http://localhost:8000", description="M1 FastAPI backend service URL")
    USERNAME: str = Field(default="operator_user", description="Authentication username for AI event dispatcher")
    PASSWORD: str = Field(default="OperatorSecret123!", description="Authentication password for AI event dispatcher")
    CAMERA_ID: Optional[str] = Field(default=None, description="Backend UUID of camera stream being analyzed")
    ZONE_ID: Optional[str] = Field(default=None, description="Backend UUID of target restricted zone")
    DISPATCH_TIMEOUT: float = Field(default=5.0, description="HTTP timeout for event dispatch requests in seconds")
    DISPATCH_RETRIES: int = Field(default=3, description="Maximum retry attempts for failed event dispatches")
    DISPATCH_QUEUE_SIZE: int = Field(default=100, description="Maximum bounded queue size for background event dispatching")

    model_config = SettingsConfigDict(
        env_prefix="AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


ai_settings = AISettings()

