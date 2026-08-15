from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.category import router as category_router
from app.api.product import router as product_router

app = FastAPI(
    title="SpiceFlow API",
    description="Backend API for the SpiceFlow organic masala business",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)

@app.get("/")
def root():
    return {
        "message": "SpiceFlow API is running"
    }