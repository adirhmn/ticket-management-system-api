from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Generic, TypeVar, List


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100, description="Name of the customer reporting the issue")
    customer_email: EmailStr = Field(..., description="Valid email address of the customer")
    subject: str = Field(..., min_length=1, max_length=200, description="Short summary of the issue")
    description: str = Field(..., min_length=1, description="Detailed description of the issue")

class TicketCreate(TicketBase):
    status: Optional[TicketStatus] = Field(default=TicketStatus.OPEN, description="Initial ticket status")
    priority: Optional[TicketPriority] = Field(default=TicketPriority.LOW, description="Priority rating")

class TicketUpdate(BaseModel):
    customer_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    customer_email: Optional[EmailStr] = None
    subject: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None

class TicketResponse(TicketBase):
    id: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# Generic Response Wrapper Types
T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T

class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class PaginatedApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: List[T]
    pagination: PaginationInfo

