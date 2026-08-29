import io
import base64
import pyotp
import qrcode
from qrcode.image.pil import PilImage


class MfaService:
    @staticmethod
    def generate_totp_secret() -> str:
        """
        Generates a secure random 32-character base32 TOTP secret.
        """
        return pyotp.random_base32()

    @staticmethod
    def generate_provisioning_uri(username: str, secret: str, issuer: str = "IBVAP Border Security") -> str:
        """
        Generates standard RFC 6238 TOTP provisioning URI compatible with Google Authenticator,
        Microsoft Authenticator, Authy, and 1Password.
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)

    @staticmethod
    def generate_qr_code_base64(provisioning_uri: str) -> str:
        """
        Renders a high-contrast QR code image as a base64 data URL string for instant frontend rendering.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=3,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img: PilImage = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_totp_code(secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Cryptographically verifies the 6-digit TOTP code against the shared secret.
        valid_window=1 allows +-30 seconds clock drift tolerance.
        """
        if not secret or not code:
            return False
        # Normalize code (strip whitespace)
        clean_code = str(code).strip().replace(" ", "").replace("-", "")
        if not clean_code.isdigit() or len(clean_code) != 6:
            return False

        totp = pyotp.TOTP(secret)
        return totp.verify(clean_code, valid_window=valid_window)
