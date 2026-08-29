"""IBVAP camera ingestion module."""

from ai.camera.base import CameraSource
from ai.camera.file import VideoFileSource
from ai.camera.synthetic import SyntheticSource
from ai.camera.webcam import WebcamSource

__all__ = [
    "CameraSource",
    "WebcamSource",
    "VideoFileSource",
    "SyntheticSource",
]
