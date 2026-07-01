from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app import models, schemas

def escape_like_value(val: str) -> str:
    """
    Escapes special SQL wildcard characters (like '%' and '_') to prevent
    unexpected broad matching and logical query bugs in LIKE/ILIKE queries.
    """
    return val.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

def get_ticket(db: Session, ticket_id: str) -> Optional[models.Ticket]:
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def get_tickets(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    subject: Optional[str] = None,
    search: Optional[str] = None
):
    query = db.query(models.Ticket)
    
    if status:
        query = query.filter(models.Ticket.status == status)
    if customer_name:
        query = query.filter(models.Ticket.customer_name.ilike(f"%{escape_like_value(customer_name)}%", escape="\\"))
    if customer_email:
        query = query.filter(models.Ticket.customer_email.ilike(f"%{escape_like_value(customer_email)}%", escape="\\"))
    if subject:
        query = query.filter(models.Ticket.subject.ilike(f"%{escape_like_value(subject)}%", escape="\\"))
    if search:
        escaped_search = escape_like_value(search)
        query = query.filter(
            or_(
                models.Ticket.customer_name.ilike(f"%{escaped_search}%", escape="\\"),
                models.Ticket.customer_email.ilike(f"%{escaped_search}%", escape="\\"),
                models.Ticket.subject.ilike(f"%{escaped_search}%", escape="\\"),
                models.Ticket.description.ilike(f"%{escaped_search}%", escape="\\")
            )
        )

    
    # Count total items matching the filters (before applying pagination offset/limit)
    total_items = query.count()
    
    # Calculate offset
    offset = (page - 1) * page_size
    items = query.order_by(models.Ticket.created_at.desc()).offset(offset).limit(page_size).all()
    
    return items, total_items


def create_ticket(db: Session, ticket: schemas.TicketCreate) -> models.Ticket:
    db_ticket = models.Ticket(
        customer_name=ticket.customer_name,
        customer_email=ticket.customer_email,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status.value if ticket.status else "open",
        priority=ticket.priority.value if ticket.priority else "low"
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def update_ticket(db: Session, ticket_id: str, ticket_update: schemas.TicketUpdate) -> Optional[models.Ticket]:
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    
    # Exclude unset fields (only update what is passed in PATCH)
    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            # Enums should be saved as string values in database
            if hasattr(value, "value"):
                setattr(db_ticket, key, value.value)
            else:
                setattr(db_ticket, key, value)
                
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def delete_ticket(db: Session, ticket_id: str) -> Optional[models.Ticket]:
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    db.delete(db_ticket)
    db.commit()
    return db_ticket
