from fastapi import FastAPI
from app.api.v1.endpoints import book, user

app = FastAPI()
app.include_router(book.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
 

@app.get("/")
def health():
    return {"code": 0, "data": "Hello World!"}
 


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)