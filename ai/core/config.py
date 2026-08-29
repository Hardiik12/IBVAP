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

    model_config = SettingsConfigDict(
        env_prefix="AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


ai_settings = AISettings()
