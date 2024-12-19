# database.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker


# Настройка SQLite базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель Product
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    name = Column(String, index=True)
    price = Column(Integer)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Работа с продуктами
def create_product(db: Session, brand: str, name: str, price: int):
    # Проверка, существует ли продукт с таким же брендом, названием, ценой
    existing_product = db.query(Product).filter_by(brand=brand, name=name, price=price).first()

    # Если продукт уже существует, то не записываем его в базу второй раз
    if existing_product:
        print(f"Продукт {name} бренда {brand}  с ценой {price} уже существует в базе данных.")
        return existing_product

    db_product = Product(brand=brand, name=name, price=price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        return product
    else:
        return None

def update_product(db: Session, product_id: int, name: str = None, price: int = None, brand: str = None):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        if name:
            product.name = name
        if price:
            product.price = price
        if brand:
            product.brand = brand

        db.commit()
        db.refresh(product)
        return product
    else:
        return None

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return "Продукт удален"
    return None
