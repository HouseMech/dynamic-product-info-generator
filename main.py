from typing import Union
from dotenv import load_dotenv
from fastapi import FastAPI
import openai

load_dotenv()

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/getProductInfo/{item_name}")
def generate_mock_product(item_name: str, q: Union[str, None] = None):
    return {
        "product": {
            "id": "12345",
            "name": "RoboBuddy 3000",
            "description": "An interactive robot toy with AI-powered responses and educational games.",
            "category": "Toys & Games",
        }
    }