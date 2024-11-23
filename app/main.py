from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from parser import get_all_products
from database import SessionLocal, Product, create_product, get_products, update_product, delete_product

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Фоновая задача для парсинга и сохранения продуктов в базе данных
def background_parse(db: Session):
    products, _ = get_all_products()
    for product in products:
        create_product(db, brand=product["brand"], name=product["name"], price=product["price"])
    print("Записали товары в базу")

@app.get("/parse")
async def parse_products(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(background_parse, db)
    return {"status": "Парсинг запущен в фоновом режиме"}


@app.get("/get-products")
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_products(db, skip=skip, limit=limit)

@app.put("/products/{product_id}")
def edit_product(product_id: int, name: str, price: int, db: Session = Depends(get_db)):
    return update_product(db, product_id, name=name, price=price)

@app.delete("/products/{product_id}")
def remove_product(product_id: int, db: Session = Depends(get_db)):
    return delete_product(db, product_id)

@app.get("/parse-products")
async def parse_products_route():
    # Получаем HTML-страницу
    products = get_all_products()

    return products
