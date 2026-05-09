from database.database import engine, Base
from database import models


# Create all PostgreSQL tables from SQLAlchemy models
def create_tables():

    print("Creating PostgreSQL tables...")

    # Generate database tables
    Base.metadata.create_all(bind=engine)

    print("Tables created successfully.")


# Run table creation directly from this file
if __name__ == "__main__":

    create_tables()