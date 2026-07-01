from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas, models
from app.database import get_db
from app.auth import get_api_key

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
    dependencies=[Depends(get_api_key)]  # Enforce API Key authentication globally for all ticket endpoints
)

@router.post("", response_model=schemas.ApiResponse[schemas.TicketResponse], status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    """
    Create a new support ticket.
    Requires authentication via X-API-Key header.
    """
    db_ticket = crud.create_ticket(db=db, ticket=ticket)
    return {
        "success": True,
        "message": "Ticket created successfully.",
        "data": db_ticket
    }

@router.get("", response_model=schemas.PaginatedApiResponse[schemas.TicketResponse])
def read_tickets(
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
    status: Optional[schemas.TicketStatus] = Query(default=None, description="Filter by ticket status"),
    customer_name: Optional[str] = Query(default=None, description="Search/Filter by customer name (partial)"),
    customer_email: Optional[str] = Query(default=None, description="Search/Filter by customer email (partial)"),
    subject: Optional[str] = Query(default=None, description="Search/Filter by subject (partial)"),
    search: Optional[str] = Query(default=None, description="Broad search query matching name, email, subject, or description"),
    db: Session = Depends(get_db)
):
    """
    Retrieve tickets with pagination and filtering/search capability.
    Requires authentication via X-API-Key header.
    """
    status_str = status.value if status else None
    tickets, total_items = crud.get_tickets(
        db=db,
        page=page,
        page_size=page_size,
        status=status_str,
        customer_name=customer_name,
        customer_email=customer_email,
        subject=subject,
        search=search
    )
    
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
    
    return {
        "success": True,
        "message": "Tickets retrieved successfully.",
        "data": tickets,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }
    }

@router.get("/{ticket_id}", response_model=schemas.ApiResponse[schemas.TicketResponse])
def read_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single ticket by its UUID.
    Requires authentication via X-API-Key header.
    """
    db_ticket = crud.get_ticket(db=db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )
    return {
        "success": True,
        "message": "Ticket retrieved successfully.",
        "data": db_ticket
    }

@router.patch("/{ticket_id}", response_model=schemas.ApiResponse[schemas.TicketResponse])
def update_ticket(ticket_id: str, ticket_update: schemas.TicketUpdate, db: Session = Depends(get_db)):
    """
    Update a ticket (PATCH - partial update).
    Requires authentication via X-API-Key header.
    """
    db_ticket = crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_update)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )
    return {
        "success": True,
        "message": "Ticket updated successfully.",
        "data": db_ticket
    }

@router.delete("/{ticket_id}", response_model=schemas.ApiResponse[dict])
def delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """
    Delete a ticket by its UUID.
    Requires authentication via X-API-Key header.
    """
    db_ticket = crud.delete_ticket(db=db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )
    return {
        "success": True,
        "message": f"Ticket with ID '{ticket_id}' has been deleted.",
        "data": {
            "id": db_ticket.id,
            "customer_name": db_ticket.customer_name,
            "subject": db_ticket.subject
        }
    }

