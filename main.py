from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, or_
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
import datetime

# --- Database Setup (SQLite) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./crm.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

# Database Models
class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True)
    customer_name = Column(String, index=True)
    customer_email = Column(String)
    subject = Column(String)
    description = Column(String)
    status = Column(String, default="Open") # Open, In Progress, Closed
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    notes = relationship("Note", back_populates="ticket")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    note_text = Column(String)
    created_at = Column(DateTime, default=get_utc_now)
    
    ticket = relationship("Ticket", back_populates="notes")

# Create tables automatically
Base.metadata.create_all(bind=engine)

# --- FastAPI App Initialization ---
app = FastAPI(title="Datastraw Support CRM")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Validation Schemas ---
class TicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str

class TicketUpdate(BaseModel):
    status: str
    notes: str | None = None

# --- Routes ---

# Serve the Frontend HTML
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

# 1. CREATE TICKET
@app.post("/api/tickets")
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = Ticket(
        customer_name=ticket.customer_name,
        customer_email=ticket.customer_email,
        subject=ticket.subject,
        description=ticket.description,
        status="Open"
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Generate the auto ticket ID like TKT-001 based on database ID
    db_ticket.ticket_id = f"TKT-{db_ticket.id:03d}"
    db.commit()
    db.refresh(db_ticket)
    
    return {"ticket_id": db_ticket.ticket_id, "created_at": db_ticket.created_at}

# 2. LIST ALL TICKETS (Includes Search & Filter)
@app.get("/api/tickets")
def get_tickets(status: str | None = None, search: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
        
    if search:
        search_fmt = f"%{search}%"
        # Search across multiple columns
        query = query.filter(
            or_(
                Ticket.customer_name.ilike(search_fmt),
                Ticket.ticket_id.ilike(search_fmt),
                Ticket.customer_email.ilike(search_fmt),
                Ticket.description.ilike(search_fmt)
            )
        )
        
    tickets = query.order_by(Ticket.created_at.desc()).all()
    return [{
        "ticket_id": t.ticket_id, 
        "customer_name": t.customer_name, 
        "subject": t.subject, 
        "status": t.status, 
        "created_at": t.created_at
    } for t in tickets]

# 3. GET SINGLE TICKET DETAILS
@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    notes_list = [{"text": n.note_text, "created_at": n.created_at} for n in ticket.notes]
    
    return {
        "ticket_id": ticket.ticket_id,
        "customer_name": ticket.customer_name,
        "customer_email": ticket.customer_email,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "notes": notes_list,
        "created_at": ticket.created_at
    }

# 4. UPDATE TICKET STATUS & ADD NOTES
@app.put("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, update_data: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update status
    if update_data.status:
        ticket.status = update_data.status
        
    # Append to Notes table if a note is provided
    if update_data.notes and update_data.notes.strip():
        new_note = Note(ticket_id=ticket.id, note_text=update_data.notes)
        db.add(new_note)
        
    db.commit()
    db.refresh(ticket)
    return {"success": True, "updated_at": ticket.updated_at}