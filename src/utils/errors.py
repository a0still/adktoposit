"""Error handling utilities for the application."""
from typing import Dict, Any, Optional
from flask import jsonify

class AppError(Exception):
    """Base application error class."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

def handle_error(error: AppError) -> tuple[Dict[str, Any], int]:
    """
    Convert application error to JSON response.
    
    Args:
        error: AppError instance
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        'status': 'error',
        'message': str(error.message),
        'details': error.details
    }
    return jsonify(response), error.status_code

class VertexAIError(AppError):
    """Vertex AI specific errors."""
    @classmethod
    def from_exception(cls, e: Exception) -> 'VertexAIError':
        """Create a VertexAIError from another exception."""
        message = str(e)
        status_code = 500
        details = {}

        if "Permission denied" in message or "not authorized" in message.lower():
            status_code = 403
            details = {
                "error_type": "permission_denied",
                "suggested_action": "Verify that the service account has the required roles (e.g., ML Admin) and wait for permission propagation"
            }
        elif "not found" in message.lower():
            status_code = 404
            details = {
                "error_type": "resource_not_found",
                "suggested_action": "Verify the model name and version are correct and accessible"
            }
        elif "quota" in message.lower():
            status_code = 429
            details = {
                "error_type": "quota_exceeded",
                "suggested_action": "Check quota limits and request increases if needed"
            }
        
        return cls(message, status_code=status_code, details=details)

class DataError(AppError):
    """Data handling and processing errors."""
    pass

class ConfigError(AppError):
    """Configuration related errors."""
    pass

class AuthError(AppError):
    """Authentication and authorization errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=401,
            details=details or {
                "error_type": "authentication_error",
                "suggested_actions": [
                    "Verify service account key file exists and is valid",
                    "Check if required APIs are enabled",
                    "Ensure service account has necessary permissions",
                    "Wait for permission changes to propagate (can take up to 15 minutes)"
                ]
            }
        )