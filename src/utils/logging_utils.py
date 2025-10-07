"""Logging configuration and utilities for the application."""
import logging
import logging.handlers
import os
import uuid
from datetime import datetime
from typing import Optional
from functools import wraps
from flask import request, has_request_context, g

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure formatters
DETAILED_FORMATTER = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] '
    '%(name)s - %(message)s'
)

# Create handlers
def setup_file_handler(filename: str, level: int = logging.INFO) -> logging.Handler:
    """Create a rotating file handler."""
    handler = logging.handlers.RotatingFileHandler(
        os.path.join(logs_dir, filename),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    handler.setLevel(level)
    handler.setFormatter(DETAILED_FORMATTER)
    return handler

# Create loggers
app_logger = logging.getLogger('app')
auth_logger = logging.getLogger('auth')
vertex_logger = logging.getLogger('vertex')

# Set up handlers
app_logger.addHandler(setup_file_handler('app.log'))
auth_logger.addHandler(setup_file_handler('auth.log'))
vertex_logger.addHandler(setup_file_handler('vertex.log'))

# Set log levels
app_logger.setLevel(logging.INFO)
auth_logger.setLevel(logging.DEBUG)  # More detailed logging for auth issues
vertex_logger.setLevel(logging.DEBUG)  # More detailed logging for Vertex AI issues

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request ID and context."""
    
    def format(self, record):
        """Format the log record with request context."""
        if has_request_context():
            record.request_id = getattr(g, 'request_id', 'no-request-id')
            record.context = {
                'path': request.path,
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }
        else:
            record.request_id = 'no-request-id'
            record.context = {}
            
        return super().format(record)

def log_exception(exc: Exception, context: Optional[dict] = None) -> None:
    """
    Log an exception with additional context.
    
    Args:
        exc: The exception to log
        context: Additional context to include in the log
    """
    ctx = {
        'timestamp': datetime.utcnow().isoformat(),
        'exception_type': exc.__class__.__name__,
        'exception_message': str(exc)
    }
    
    if context:
        ctx.update(context)
    
    if isinstance(exc, PermissionError) or 'permission' in str(exc).lower():
        auth_logger.error(
            "Permission error occurred",
            extra={
                'context': ctx,
                'request_id': getattr(g, 'request_id', 'no-request-id')
            },
            exc_info=True
        )
    else:
        app_logger.error(
            "An error occurred",
            extra={
                'context': ctx,
                'request_id': getattr(g, 'request_id', 'no-request-id')
            },
            exc_info=True
        )

def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())

def log_api_call(func):
    """Decorator to log API calls with timing and context."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        
        if has_request_context():
            g.request_id = generate_request_id()
            app_logger.info(
                f"API call started: {request.method} {request.path}",
                extra={
                    'context': {
                        'method': request.method,
                        'path': request.path,
                        'args': request.args.to_dict(),
                        'start_time': start_time.isoformat()
                    },
                    'request_id': g.request_id
                }
            )
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            if has_request_context():
                app_logger.info(
                    f"API call completed: {request.method} {request.path}",
                    extra={
                        'context': {
                            'duration': duration,
                            'status_code': getattr(result, 'status_code', 'unknown')
                        },
                        'request_id': g.request_id
                    }
                )
            
            return result
            
        except Exception as e:
            log_exception(e, {
                'duration': (datetime.utcnow() - start_time).total_seconds()
            })
            raise
        
    return wrapper

def log_vertex_operation(operation_name: str):
    """Decorator to log Vertex AI operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            vertex_logger.info(
                f"Vertex AI operation started: {operation_name}",
                extra={
                    'context': {
                        'operation': operation_name,
                        'start_time': start_time.isoformat(),
                        'args': str(args),
                        'kwargs': str(kwargs)
                    },
                    'request_id': getattr(g, 'request_id', 'no-request-id')
                }
            )
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                vertex_logger.info(
                    f"Vertex AI operation completed: {operation_name}",
                    extra={
                        'context': {
                            'operation': operation_name,
                            'duration': duration,
                            'success': True
                        },
                        'request_id': getattr(g, 'request_id', 'no-request-id')
                    }
                )
                
                return result
                
            except Exception as e:
                vertex_logger.error(
                    f"Vertex AI operation failed: {operation_name}",
                    extra={
                        'context': {
                            'operation': operation_name,
                            'duration': (datetime.utcnow() - start_time).total_seconds(),
                            'error': str(e),
                            'error_type': e.__class__.__name__
                        },
                        'request_id': getattr(g, 'request_id', 'no-request-id')
                    },
                    exc_info=True
                )
                raise
                
        return wrapper
    return decorator