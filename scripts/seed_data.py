from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.product import Product
from app.models.user import User


def seed(db: Session) -> None:
    admin = db.query(User).filter(User.email == "admin@cloudcart.com").first()
    if not admin:
        db.add(
            User(
                full_name="CloudCart Admin",
                email="admin@cloudcart.com",
                hashed_password=hash_password("Admin@12345"),
                is_admin=True,
                address="HQ, Bengaluru",
            )
        )
        db.commit()

    if db.query(Product).count() == 0:
        products = [
            Product(
                name="Wireless Keyboard",
                description="Ergonomic Bluetooth keyboard for daily work.",
                category="Electronics",
                price=39.99,
                rating=4.4,
                stock=40,
            ),
            Product(
                name="Running Shoes",
                description="Comfortable lightweight shoes for workouts.",
                category="Sports",
                price=59.99,
                rating=4.7,
                stock=25,
            ),
            Product(
                name="Steel Water Bottle",
                description="Insulated bottle with 24-hour cooling support.",
                category="Lifestyle",
                price=19.5,
                rating=4.2,
                stock=100,
            ),
        ]
        db.add_all(products)
        db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
        print("Seed complete. Admin: admin@cloudcart.com / Admin@12345")
    finally:
        db.close()
