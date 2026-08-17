"""Models package initialization."""
# Import all models to ensure they're registered with SQLAlchemy Base
from app.models.user import UserDB
from app.models.ticket import TicketDB

__all__ = ['UserDB', 'TicketDB']
