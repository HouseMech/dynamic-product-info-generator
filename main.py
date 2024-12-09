from dotenv import load_dotenv
from fastapi import FastAPI
import os
import json
import openai
import requests
from bs4 import BeautifulSoup

load_dotenv()

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY", "default-key")
if openai.api_key == "default-key" or openai.api_key == "":
    raise ValueError('OPENAI_API_KEY is empty!')

# MOCK ENDPOINT: Connect to GPT and have it return product data from a name.
@app.get("/getMockProductInfo/{item_name}")
def generate_mock_product(item_name: str):
    try:
        # Construct the prompt
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that generates accurate and detailed product information and returns it in JSON format. Only provide information if you are certain it is accurate. Example: For a product 'XYZ', provide this JSON structure: { 'id': '...', 'name': '...', 'description': '...', 'specifications': 'Data not available' }"
            },
            {
                "role": "user",
                "content": f"Generate detailed product information for a product named '{item_name}'. Provide placeholder text for missing data instead of fabricating it."
            }
        ]

        # Call the ChatCompletion API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.5,
            logprobs=True,
            top_logprobs=5
        )

        # return {"product_name": item_name, "details": product_info}
        product_info = response.choices[0].message.content.strip()

        return {"product_name": item_name, "details": json.loads(product_info), "response": response}
    except Exception as e:
        return {"error": str(e)}
# MASTER FUNCTION, calls the other functions.
# After passing in a product name via a search query, first it attempts to search the Amazon store (via webscraping, if I had the time to get access to Amazon's Product Advertising API that would have been a nice avenue to explore as well.)
# Afterwards, it accesses the product page for the item found, and acquires information from the page such as title, price and product info.
# Afterwards, it sends that collected data to GPT to organize into JSON format.
@app.get("/getProductInfo/{item_name}")
def generate_product_json(item_name: str):
    amazon_product = search_amazon(item_name)
    gpt_data = None
    error = False
    if amazon_product:
        if "error" in amazon_product:
            error = True
        else:
            # Scrape data send to GPT
            amazon_data = scrape_amazon_product(amazon_product["link"])
            gpt_data = generate_product_data_from_info(amazon_data)
            return gpt_data
    else:
        error = True
    if error:
        return {"error": "Failed to get product data"}

# Define headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
    
}
# Use Amazon search to find products
# In the interest of saving time, I only used Amazon instead of multiple solutions. If I had more time to allot to this project I would have used multiple sources.
# In addition, this code only grabs the first result that it finds from amazon's list - which can sometimes change even if searching with an identical query. This shortcoming would be another thing I would ameliorate with more time.
def search_amazon(product_name):
    # Construct the search URL
    query = product_name.replace(" ", "+")
    search_url = f"https://www.amazon.ca/s?k={query}"

    # Make the request
    response = requests.get(search_url, headers=HEADERS)
    response.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the first product link
    product = soup.find("div", {"class": "s-main-slot"}).find("div", {"data-component-type": "s-search-result"})
    title = None
    if product:
        title_element = product.find("span", {"class": "a-size-medium"})
        if title_element: 
           title = title_element.get_text(strip=True) 
        else:
            title = product_name
        link = "https://www.amazon.ca" + product.find("a", {"class": "a-link-normal"})["href"]
        return {"title": title, "link": link}
    else:
        return {"error": "No results found"}
# Send the product data collected from Amazon to GPT to be organized into JSON format.
def generate_product_data_from_info(product_data):
    prompt = (
        f"Based on the following product data, generate a detailed description:\n\n"
        f"Name: {product_data['title']}\n"
        f"Price: {product_data['price']}\n\n"
        f"Description: {product_data['description']}\n\n"
        f"Details: {product_data['details']}\n\n"
        f"Provide Pricing, specifications, features, and a review summary. Ensure this is in JSON format."
    )
    try:
        # Construct the prompt
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that generates accurate and detailed product information and returns it in JSON format. Only provide information if you are certain it is accurate. Example: For a product 'XYZ', provide this JSON structure: { 'id': '...', 'name': '...', 'description': '...', 'specifications': 'Data not available' }"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Call the ChatCompletion API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=750,
            temperature=0.5,
            logprobs=True,
            top_logprobs=5
        )
        product_info = response.choices[0].message.content.strip()
        return {"product_name": product_data['title'], "details": json.loads(product_info), "response": response}
    except Exception as e:
        return {"error": str(e)}
def scrape_amazon_product(url):
    try:
        # Make the request
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.content, "lxml")

        # Extract product details
        product = {}

        # Product Title
        title = soup.find("span", {"id": "productTitle"})
        product["title"] = title.get_text(strip=True) if title else "N/A"

        # Product Price
        price = soup.find("span", {"class": "a-price-whole"})
        product["price"] = price.get_text(strip=True) if price else "N/A"

        # Product Description
        description = soup.find("div", {"id": "feature-bullets"})
        product["description"] = (
            description.get_text(strip=True) if description else "N/A"
        )

        # Product Details
        details = soup.find("div", {"id": "prodDetails"})
        product["details"] = (
            details.get_text(strip=True) if details else "N/A"
        )

        return product

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
