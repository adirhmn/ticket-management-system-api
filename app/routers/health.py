from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from datetime import datetime, timezone
from app.database import get_db

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Unauthenticated health status endpoint.
    Performs a database ping check to ensure underlying storage services are online.
    """
    try:
        # Ping the database using a simple SELECT 1 query
        db.execute(text("SELECT 1"))
    except Exception as e:
        # Return 503 if the database is unreachable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed."
        )
        
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


