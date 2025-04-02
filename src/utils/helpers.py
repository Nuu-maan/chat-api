import json
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO format"""
    return dt.isoformat()

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO format timestamp to datetime"""
    return datetime.fromisoformat(timestamp_str)

def sanitize_message_content(content: str) -> str:
    """Sanitize message content"""
    return content.strip()

def create_error_response(message: str, code: int = 400) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "error": {
            "code": code,
            "message": message,
            "timestamp": format_timestamp(datetime.utcnow())
        }
    }

def create_success_response(data: Any) -> Dict[str, Any]:
    """Create a standardized success response"""
    return {
        "data": data,
        "timestamp": format_timestamp(datetime.utcnow())
    }

def validate_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate and sanitize metadata"""
    if metadata is None:
        return {}
    
    # Convert to JSON and back to ensure serializable
    try:
        return json.loads(json.dumps(metadata))
    except (TypeError, json.JSONDecodeError):
        return {} 