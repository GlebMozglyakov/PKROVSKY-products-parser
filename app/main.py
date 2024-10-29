from fastapi import FastAPI
from parser import get_all_products

app = FastAPI()

@app.get("/parse-products")
async def parse_products_route():
    # Получаем HTML-страницу
    products = get_all_products()

    return products
