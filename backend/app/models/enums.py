import enum


class CameraSourceType(str, enum.Enum):
    WEBCAM = "WEBCAM"
    VIDEO_FILE = "VIDEO_FILE"
    RTSP = "RTSP"


class ZoneType(str, enum.Enum):
    RESTRICTED = "RESTRICTED"
    MONITORED = "MONITORED"


class EventType(str, enum.Enum):
    INTRUSION = "INTRUSION"
    EXIT = "EXIT"
    LOITERING = "LOITERING"
    UNAUTHORIZED_VEHICLE = "UNAUTHORIZED_VEHICLE"


class EventSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventStatus(str, enum.Enum):
    NEW = "NEW"
    PROCESSED = "PROCESSED"
    ARCHIVED = "ARCHIVED"


class AlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class UserRole(str, enum.Enum):
    OPERATOR = "OPERATOR"
    ANALYST = "ANALYST"
    ADMINISTRATOR = "ADMINISTRATOR"
    AUDITOR = "AUDITOR"
