import requests
from bs4 import BeautifulSoup
from schemas import ProductBase
import json
from database import create_product
from sqlalchemy.orm import Session


def fetch_page(url):
    """
    Функция получения страницы
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Ошибка при загрузке страницы: {response.status_code}")
        return None


def parse_products_from_cur_page(html):
    """
    Парсим продукты со страницы
    """
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    pydantic_products = []

    # Задаем селектор для карточек товаров
    product_cards = soup.select(".ProductCard_product__2sBWu")

    for card in product_cards:
        # Извлекаем название и бренд
        brand = card.select_one(".ProductCard_product__brand__WozgB").get_text(strip=True) if card.select_one(
            ".ProductCard_product__brand__WozgB") else "Бренд не найден"
        title = card.select_one(".heading_heading_5__sKtfG").get_text(strip=True) if card.select_one(
            ".heading_heading_5__sKtfG") else "Название не найдено"

        # Извлекаем цену
        price = card.select_one(".ProductCard_product__price__8Yr1C").get_text(strip=True) if card.select_one(
            ".ProductCard_product__price__8Yr1C") else "Цена не указана"

        price = int(price.replace('₽', '').replace(' ', '').strip())

        # Добавляем данные в список
        products.append({
            "brand": brand,
            "name": title,
            "price": price
        })

        pydantic_products.append(
            ProductBase(brand=brand, name=title, price=price)
        )


    return products, pydantic_products


def write_products_to_json(all_products):
    with open('data/products.json', 'w', encoding='utf-8') as file:
        json.dump(all_products, file, ensure_ascii=False, indent=4)


def write_products_to_db(db: Session, parsed_products):
    # Проход по страницам и сохранение в базу
    for product in parsed_products:
        create_product(db, brand=product["brand"], name=product["name"], price=product["price"])


def get_all_products():
    """
    Проходимся по всем страницам в новинках
    """
    base_url = "https://pkrovsky.com/men/new/"
    page_number = 1
    all_products = []
    all_pydantic_products = []

    while True:
        url = f"{base_url}?page={page_number}"
        print(f"Сбор данных со страницы: {url}")

        html = fetch_page(url)
        if html is None:
            break

        products, pydantic_products = parse_products_from_cur_page(html)
        if not products:
            print("Товары не найдены, завершение парсинга.")
            break

        all_products.extend(products)
        all_pydantic_products.extend(pydantic_products)
        page_number += 1

    print(len(all_products))

    # Записываем товары в json
    # write_products_to_json(all_products)
    # write_products_to_db(db, all_products)

    return all_products, all_pydantic_products


# Запуск парсера
# products, pydantic_products = get_all_products()

# Вывод собранных данных
# for product in products:
#     print(f"Название: {product['name']}, Бренд: {product['brand']}, Цена: {product['price']}")

# print(f"len {len(pydantic_products)}")
#
# for product in pydantic_products:
#     print(product)
