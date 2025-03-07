from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, validator
import uuid

def generate_id() -> str:
    """Generate a unique ID for database objects."""
    return str(uuid.uuid4())

class TimestampModel(BaseModel):
    """Base model with creation and update timestamps."""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

class DBModel(TimestampModel):
    """Base model for database objects with ID."""
    id: str = Field(default_factory=generate_id)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True 