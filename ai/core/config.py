from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """
    AI Processing Engine Settings.
    Loads values from environment variables or .env file.
    """
    SOURCE_TYPE: str = Field(default="WEBCAM", description="Camera source type: WEBCAM, VIDEO_FILE, RTSP, or SYNTHETIC")
    CAMERA_INDEX: int = Field(default=0, description="Device index for webcam ingestion (e.g. 0, 1)")
    VIDEO_PATH: Optional[str] = Field(default=None, description="Path to local video file for VIDEO_FILE mode")
    FRAME_WIDTH: Optional[int] = Field(default=None, description="Target width for frame processing/display")
    FRAME_HEIGHT: Optional[int] = Field(default=None, description="Target height for frame processing/display")
    DISPLAY_PREVIEW: bool = Field(default=True, description="Enable GUI window live preview with overlays")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    MODEL_SHA256: Optional[str] = Field(default=None, description="Expected SHA-256 digest of YOLO weights (optional verification)")

    # RTSP IP Camera Settings
    RTSP_URL: Optional[str] = Field(default=None, description="RTSP stream URL for RTSP mode (e.g. rtsp://user:pass@host:554/stream)")
    RTSP_TRANSPORT: str = Field(default="tcp", description="RTSP transport protocol: tcp or udp")
    RTSP_TIMEOUT: int = Field(default=5000000, description="RTSP socket timeout in microseconds (default 5.0s)")
    RTSP_STALE_TIMEOUT: float = Field(default=3.0, description="Duration in seconds without frames before stream is flagged STALE")
    RTSP_RECONNECT_INITIAL_DELAY: float = Field(default=1.0, description="Initial reconnect delay in seconds")
    RTSP_RECONNECT_MAX_DELAY: float = Field(default=30.0, description="Maximum reconnect delay in seconds (exponential backoff ceiling)")

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
