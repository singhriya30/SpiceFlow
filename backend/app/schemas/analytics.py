from decimal import Decimal
from pydantic import BaseModel

import uuid
from decimal import Decimal

from datetime import date


class SummaryResponse(BaseModel):
    total_revenue: Decimal
    total_orders: int
    orders_by_status: dict[str, int]



class TopProductResponse(BaseModel):
    product_id: uuid.UUID
    product_name: str
    total_quantity_sold: int
    total_revenue: Decimal

class TopCategoryResponse(BaseModel):
    category_id: uuid.UUID
    category_name: str
    total_quantity_sold: int
    total_revenue: Decimal



class SalesOverTimeResponse(BaseModel):
    date: date
    order_count: int
    revenue: Decimal

class TopCustomerResponse(BaseModel):
    customer_id: uuid.UUID
    customer_name: str
    total_spent: Decimal
    order_count: int


class CustomerStatsResponse(BaseModel):
    total_customers: int
    top_customers: list[TopCustomerResponse]