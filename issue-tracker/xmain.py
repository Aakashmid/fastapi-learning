#  this is like a hello world app for fastapi  


from fastapi import FastAPI

app = FastAPI(
    title="Issue Tracker API",
    version="0.1.0",
    description="A mini production-style API built with FastAPI",
)


items = [
    {"id": 1, "name": "Issue 1", "status": "open"},
    {"id": 2, "name": "Issue 2", "status": "closed"},
    {"id": 3, "name": "Issue 3", "status": "in progress"},
]


# example routes 

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/items")
def get_items():
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}


# get request  for query parameters  like - /items?page=2&limit=5  
@app.get("/items")
def get_items(page: int = 1, limit: int = 10):
    start = (page - 1) * limit
    end = start + limit
    return items[start:end]


# post request example 
@app.post("/items")
def create_item(item: dict):  # it can get any dict as we didn't use pydantic for data type 
    items.append(item)
    return item