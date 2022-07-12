from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/smartphones")
async def root(price: int = None):
    with open('smartphones.json') as json_file:
       data = json.load(json_file)

    if price:
        res = [x for x in data if x['price'] == price]
        return res

    return data
