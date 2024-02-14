# Import necessary libraries and modules

# pip install fastapi uvicorn[standard] sqlalchemy databases[sqlite] pydantic

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from databases import Database
from datetime import datetime
from pydantic import BaseModel
from typing import List

# Define the database URL
DATABASE_URL = "sqlite:///./test.db"

# Create an instance of the SQLAlchemy Base class
Base = declarative_base()

# Define the SQLAlchemy model for the Book table
class Book(Base):
    __tablename__ = "books"  # Set the table name

    # Define columns for the Book table
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    published_date = Column(DateTime, default=datetime.utcnow)

# Create a FastAPI application
app = FastAPI()

# Create a Database instance with the specified database URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()  # Create a new session using SessionLocal
    try:
        yield db  # Provide the database session to the dependent function
    finally:
        db.close()  # Close the database session when the operation is finished

# Pydantic model for input validation when creating a book
class BookCreate(BaseModel):
    title: str
    author: str

# Pydantic model for the response when retrieving a book
class BookResponse(BookCreate):
    id: int
    published_date: datetime

# API endpoint to create a new book
@app.post("/books/", response_model=BookResponse)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())  # Create a SQLAlchemy Book instance from the Pydantic model
    db.add(db_book)  # Add the Book instance to the database session
    db.commit()  # Commit the changes to the database
    db.refresh(db_book)  # Refresh the Book instance to reflect changes from the database
    return db_book  # Return the created book

# API endpoint to get all books
@app.get("/books/", response_model=List[BookResponse])
async def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()  # Query all books from the database and return the result
