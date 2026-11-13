
from getpass import getpass

from sqlalchemy import inspect, text

from app.database import engine, SessionLocal, Base
from app import models
from app.models import User
from app.services.auth_service import hash_password


def initialize_database():
    # Create any missing tables
    Base.metadata.create_all(bind=engine)

    # Check existing bookings table
    inspector = inspect(engine)

    columns = [
        column["name"]
        for column in inspector.get_columns("bookings")
    ]

    # Add user_id if it does not exist
    if "user_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE bookings "
                    "ADD COLUMN user_id INTEGER "
                    "REFERENCES users(id)"
                )
            )

        print("Added user_id column to bookings table.")
    else:
        print("user_id column already exists.")


def create_admin():
    initialize_database()

    print("\n===== BUSGO ADMIN ACCOUNT SETUP =====")

    full_name = input("Admin full name: ").strip()
    email = input("Admin email: ").strip().lower()

    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if len(full_name) < 2:
        print("Name must contain at least 2 characters.")
        return

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            print("An account with this email already exists.")
            return

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("\nAdmin account created successfully!")

    except Exception as error:
        db.rollback()
        print("Admin creation failed:", error)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
