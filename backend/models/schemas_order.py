"""Order-specific Pydantic schemas for CRUD operations."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """Schema for creating/importing an order."""

    order_id: str = Field(..., description="外部订单号")
    user_id: str = Field("default", description="用户 ID")
    status: str = Field("pending", description="订单状态")
    product_name: str = Field(..., description="商品名称")
    price: float = Field(..., gt=0, description="单价")
    quantity: int = Field(1, ge=1, description="数量")
    total_amount: float = Field(..., gt=0, description="总金额")
    shipping_address: Optional[str] = None
    logistics_company: Optional[str] = None
    tracking_number: Optional[str] = None
    source: str = Field("manual", description="订单来源: manual/taobao/jd/etc")


class OrderUpdate(BaseModel):
    """Schema for updating order fields."""

    status: Optional[str] = None
    logistics_company: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_address: Optional[str] = None
    return_reason: Optional[str] = None
    refund_amount: Optional[float] = None


class OrderResponse(BaseModel):
    """Schema for order detail response."""

    model_config = {"from_attributes": True}

    order_id: str
    user_id: str
    status: str
    product_name: str
    price: float
    quantity: int
    total_amount: float
    created_at: datetime
    updated_at: datetime
    shipping_address: Optional[str] = None
    logistics_company: Optional[str] = None
    tracking_number: Optional[str] = None
    return_reason: Optional[str] = None
    refund_amount: Optional[float] = None
    source: str = "manual"


class OrderListResponse(BaseModel):
    """Paginated order list."""

    total: int
    page: int
    page_size: int
    orders: list[OrderResponse]
