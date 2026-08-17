from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.category import router as category_router
from app.api.product import router as product_router
from app.api.inventory import router as inventory_router
from app.api.address import router as address_router
from app.api.review import router as review_router
from app.api.order import router as order_router
from app.api.analytics import router as analytics_router

app = FastAPI(
    title="SpiceFlow API",
    description="Backend API for the SpiceFlow organic masala business",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(inventory_router)
app.include_router(address_router)
app.include_router(review_router)
app.include_router(order_router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {
        "message": "SpiceFlow API is running"
    }