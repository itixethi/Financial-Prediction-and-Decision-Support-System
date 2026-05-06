from database.database import engine, Base
from database import models


def create_tables():
    print("Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


if __name__ == "__main__":
    create_tables()
