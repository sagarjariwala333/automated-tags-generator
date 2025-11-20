from typing import Any, Optional
from pydantic import BaseModel


class JsonResponse(BaseModel):
    """
    Standardized JSON response utility class for API responses.
    
    Fields:
        success (bool): Indicates if the operation was successful
        status (int): HTTP status code (e.g., 200, 400, 500)
        data (Any): The response payload/data (can be dict, list, str, etc.)
        error (Optional[str]): Error message if operation failed, None otherwise
    """
    success: bool
    status: int
    data: Any = None
    error: Optional[str] = None
    
    @classmethod
    def success_response(cls, data: Any, status: int = 200) -> "JsonResponse":
        """
        Create a successful response.
        
        Args:
            data: The response data
            status: HTTP status code (default: 200)
            
        Returns:
            JsonResponse instance with success=True
        """
        return cls(
            success=True,
            status=status,
            data=data,
            error=None
        )
    
    @classmethod
    def error_response(cls, error: str, status: int = 400, data: Any = None) -> "JsonResponse":
        """
        Create an error response.
        
        Args:
            error: Error message
            status: HTTP status code (default: 400)
            data: Optional data to include with error
            
        Returns:
            JsonResponse instance with success=False
        """
        return cls(
            success=False,
            status=status,
            data=data,
            error=error
        )
    
    def to_dict(self) -> dict:
        """
        Convert the response to a dictionary.
        
        Returns:
            Dictionary representation of the response
        """
        return {
            "success": self.success,
            "status": self.status,
            "data": self.data,
            "error": self.error
        }
