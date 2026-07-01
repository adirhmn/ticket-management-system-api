import uuid
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    customer_name = Column(String, nullable=False, index=True)
    customer_email = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open", index=True)
    priority = Column(String, nullable=False, default="low", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# Trigram GIN indexes for fast partial text searches in PostgreSQL (safely ignored by SQLite in tests)
Index(
    "ix_ticket_customer_name_trgm",
    Ticket.customer_name,
    postgresql_using="gin",
    postgresql_ops={"customer_name": "gin_trgm_ops"}
)
Index(
    "ix_ticket_customer_email_trgm",
    Ticket.customer_email,
    postgresql_using="gin",
    postgresql_ops={"customer_email": "gin_trgm_ops"}
)
Index(
    "ix_ticket_subject_trgm",
    Ticket.subject,
    postgresql_using="gin",
    postgresql_ops={"subject": "gin_trgm_ops"}
)
Index(
    "ix_ticket_description_trgm",
    Ticket.description,
    postgresql_using="gin",
    postgresql_ops={"description": "gin_trgm_ops"}
)

