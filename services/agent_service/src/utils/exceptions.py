"""
Custom exception classes for the agent service.
Provides structured error handling and meaningful error messages.
"""

from enum import Enum
from typing import Any, Dict, Optional, List


class ErrorSeverity(Enum):
    """Error severity levels for frontend handling."""
    LOW = "low"           # Warning, can continue
    MEDIUM = "medium"     # Issue, may affect quality
    HIGH = "high"         # Error, partial functionality
    CRITICAL = "critical" # Fatal, complete failure


class ErrorCategory(Enum):
    """Categories of errors for better frontend handling."""
    PLANNING = "planning"
    EXECUTION = "execution"
    EVALUATION = "evaluation"
    EDITING = "editing"
    EXTERNAL_SERVICE = "external_service"
    VALIDATION = "validation"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


class AgentServiceException(Exception):
    """Base exception class for all agent service errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code
        self.details = details or {}
        self.recoverable = recoverable
        self.user_message = user_message or self._generate_user_message()
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message."""
        if self.category == ErrorCategory.PLANNING:
            return "I'm having trouble understanding your request. Could you please rephrase it?"
        elif self.category == ErrorCategory.EXECUTION:
            return "I encountered an issue while processing your request. Please try again."
        elif self.category == ErrorCategory.EVALUATION:
            return "I'm having trouble evaluating the response quality. The answer may need review."
        elif self.category == ErrorCategory.EXTERNAL_SERVICE:
            return "One of my data sources is temporarily unavailable. Please try again later."
        elif self.category == ErrorCategory.NETWORK:
            return "I'm experiencing network connectivity issues. Please check your connection and try again."
        elif self.category == ErrorCategory.TIMEOUT:
            return "The request is taking longer than expected. Please try again."
        else:
            return "An unexpected error occurred. Please try again or contact support if the problem persists."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error": True,
            "message": self.message,
            "user_message": self.user_message,
            "category": self.category.value,
            "severity": self.severity.value,
            "error_code": self.error_code,
            "details": self.details,
            "recoverable": self.recoverable,
            "type": self.__class__.__name__
        }


class PlanningError(AgentServiceException):
    """Raised when planning phase fails."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.PLANNING,
            severity=ErrorSeverity.HIGH,
            error_code=error_code or "PLANNING_ERROR",
            details=details,
            user_message=user_message
        )


class ExecutionError(AgentServiceException):
    """Raised when execution phase fails."""
    
    def __init__(
        self,
        message: str,
        source: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        details = details or {}
        if source:
            details["source"] = source
        
        super().__init__(
            message=message,
            category=ErrorCategory.EXECUTION,
            severity=ErrorSeverity.HIGH,
            error_code=error_code or "EXECUTION_ERROR",
            details=details,
            user_message=user_message
        )


class EvaluationError(AgentServiceException):
    """Raised when evaluation phase fails."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.EVALUATION,
            severity=ErrorSeverity.MEDIUM,
            error_code=error_code or "EVALUATION_ERROR",
            details=details,
            user_message=user_message
        )


class ExternalServiceError(AgentServiceException):
    """Raised when external services (Notion, GitHub, etc.) fail."""
    
    def __init__(
        self,
        message: str,
        service: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        details = details or {}
        details["service"] = service
        
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            error_code=error_code or f"{service.upper()}_SERVICE_ERROR",
            details=details,
            user_message=user_message or f"The {service} service is temporarily unavailable. Please try again later."
        )


class ValidationError(AgentServiceException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        details = details or {}
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            error_code=error_code or "VALIDATION_ERROR",
            details=details,
            user_message=user_message or "Please check your input and try again."
        )


class TimeoutError(AgentServiceException):
    """Raised when operations timeout."""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        details = details or {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        
        super().__init__(
            message=message,
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            error_code=error_code or "TIMEOUT_ERROR",
            details=details,
            user_message=user_message or "The request is taking longer than expected. Please try again."
        )


class NetworkError(AgentServiceException):
    """Raised when network-related errors occur."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            error_code=error_code or "NETWORK_ERROR",
            details=details,
            user_message=user_message
        )


def create_error_response(
    exception: AgentServiceException,
    trace_info: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized error response for the frontend."""
    
    response = exception.to_dict()
    
    if trace_info:
        response["trace_info"] = trace_info
    
    if session_id:
        response["session_id"] = session_id
    
    return response


def handle_agent_error(
    error: Exception,
    context: str,
    trace_info: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Convert any exception to a structured error response."""
    
    if isinstance(error, AgentServiceException):
        return create_error_response(error, trace_info, session_id)
    
    # Convert generic exceptions to structured errors
    if "timeout" in str(error).lower():
        structured_error = TimeoutError(
            message=f"Timeout in {context}: {str(error)}",
            details={"original_error": str(error), "context": context}
        )
    elif "network" in str(error).lower() or "connection" in str(error).lower():
        structured_error = NetworkError(
            message=f"Network error in {context}: {str(error)}",
            details={"original_error": str(error), "context": context}
        )
    elif "validation" in str(error).lower():
        structured_error = ValidationError(
            message=f"Validation error in {context}: {str(error)}",
            details={"original_error": str(error), "context": context}
        )
    else:
        structured_error = AgentServiceException(
            message=f"Unexpected error in {context}: {str(error)}",
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.HIGH,
            error_code="UNKNOWN_ERROR",
            details={"original_error": str(error), "context": context}
        )
    
    return create_error_response(structured_error, trace_info, session_id) 