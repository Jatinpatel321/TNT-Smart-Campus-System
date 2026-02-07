import logging
import os
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('tnt_audit')
        self.logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # File handler
        log_file = os.path.join(log_dir, f'audit_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - IP:%(ip)s - User:%(user)s'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def log_login_attempt(self, phone: str, success: bool, ip: str = "unknown"):
        """Log login attempts"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"LOGIN_ATTEMPT - Phone: {phone} - Status: {status}",
            extra={'ip': ip, 'user': phone}
        )

    def log_otp_generation(self, phone: str, ip: str = "unknown"):
        """Log OTP generation"""
        self.logger.info(
            f"OTP_GENERATED - Phone: {phone}",
            extra={'ip': ip, 'user': phone}
        )

    def log_role_change(self, admin_phone: str, target_phone: str, old_role: str, new_role: str, ip: str = "unknown"):
        """Log role changes"""
        self.logger.warning(
            f"ROLE_CHANGE - Admin: {admin_phone} - Target: {target_phone} - {old_role} -> {new_role}",
            extra={'ip': ip, 'user': admin_phone}
        )

    def log_security_event(self, event: str, phone: str = "unknown", ip: str = "unknown"):
        """Log security events"""
        self.logger.warning(
            f"SECURITY_EVENT - {event} - Phone: {phone}",
            extra={'ip': ip, 'user': phone}
        )

# Global audit logger instance
audit_logger = AuditLogger()
