import sys
from app.core.config import Settings


def test_settings_initialization() -> None:
    """
    Test 4: Settings initialize cleanly with default values.
    """
    custom_settings = Settings(APP_NAME="IBVAP Test App", LOG_LEVEL="DEBUG")
    assert custom_settings.APP_NAME == "IBVAP Test App"
    assert custom_settings.LOG_LEVEL == "DEBUG"
    assert custom_settings.VERSION == "0.1.0"


def test_clean_imports() -> None:
    """
    Test 5: Verify backend initializes cleanly without importing unneeded modules.
    """
    cv2_preloaded = "cv2" in sys.modules

    import app.main  # noqa: F401

    forbidden_modules = ["yolo", "bytetrack", "nextjs"]
    for mod in forbidden_modules:
        assert mod not in sys.modules, f"Forbidden module '{mod}' was imported into backend environment."

    if not cv2_preloaded:
        assert "cv2" not in sys.modules, "Forbidden module 'cv2' was imported into backend environment."
