from typing import Union
from dotenv import load_dotenv
from fastapi import FastAPI
import os
import json
import openai

load_dotenv()

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY", "default-key")
if openai.api_key == "default-key":
    print("HEY THERE'S NO OPENAI KEY!")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/getProductInfo/{item_name}")
def generate_mock_product(item_name: str, q: Union[str, None] = None):
    print(item_name)
    try:
        # Construct the prompt
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that generates detailed product information and returns it in JSON format."
            },
            {
                "role": "user",
                "content": f"Generate detailed product information for a product named '{item_name}', including category, description, specifications, pricing, and reviews."
            }
        ]

        # Call the ChatCompletion API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        # return {"product_name": item_name, "details": product_info}
        product_info = response.choices[0].message.content.strip()

        return {"product_name": item_name, "details": json.loads(product_info)}
    except Exception as e:
        return {"error": str(e)}