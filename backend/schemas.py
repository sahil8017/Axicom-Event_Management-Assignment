from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime


# Valid values for enums
VALID_ROLES = ["user", "vendor", "admin"]
VALID_CATEGORIES = ["Catering", "Florist", "Decoration", "Lighting"]
VALID_MEMBERSHIP_STATUS = ["pending", "active", "inactive"]
VALID_PRODUCT_STATUS = ["pending", "approved", "rejected"]
VALID_ORDER_STATUS = ["Pending", "Confirmed", "Completed", "Cancelled"]
VALID_PAYMENT_STATUS = ["pending", "completed", "failed"]
VALID_RSVP_STATUS = ["Pending", "Confirmed", "Declined"]


# ============ Auth Schemas ============
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: Literal["user", "vendor"] = "user"

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()


class VendorRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    company_name: str = Field(..., min_length=1, max_length=200)
    category: str

    @field_validator('category')
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(VALID_CATEGORIES)}')
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    user: UserResponse
    token: str


# ============ Vendor Schemas ============
class VendorCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    category: str

    @field_validator('category')
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(VALID_CATEGORIES)}')
        return v


class VendorResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    category: str
    membership_status: str
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class VendorUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = None
    membership_status: Optional[str] = None

    @field_validator('category')
    @classmethod
    def category_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(VALID_CATEGORIES)}')
        return v

    @field_validator('membership_status')
    @classmethod
    def status_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_MEMBERSHIP_STATUS:
            raise ValueError(f'Status must be one of: {", ".join(VALID_MEMBERSHIP_STATUS)}')
        return v


# ============ Item Schemas ============
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", max_length=1000)
    price: float = Field(..., gt=0, description="Price must be greater than 0")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0, description="Price must be greater than 0")
    status: Optional[str] = None

    @field_validator('status')
    @classmethod
    def status_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PRODUCT_STATUS:
            raise ValueError(f'Status must be one of: {", ".join(VALID_PRODUCT_STATUS)}')
        return v


class ItemResponse(BaseModel):
    id: int
    vendor_id: int
    name: str
    description: Optional[str]
    price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Order Schemas ============
class OrderItemCreate(BaseModel):
    item_id: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1, le=100, description="Quantity must be between 1 and 100")


class OrderCreate(BaseModel):
    vendor_id: int = Field(..., gt=0)
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    vendor_id: int
    total_amount: float
    payment_status: str
    order_status: str
    created_at: datetime
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    order_status: str

    @field_validator('order_status')
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in VALID_ORDER_STATUS:
            raise ValueError(f'Status must be one of: {", ".join(VALID_ORDER_STATUS)}')
        return v


# ============ Cart Schemas ============
class CartItemCreate(BaseModel):
    item_id: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1, le=100, description="Quantity must be between 1 and 100")


class CartItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    item: Optional[ItemResponse] = None

    class Config:
        from_attributes = True


# ============ Guest List Schemas ============
class GuestCreate(BaseModel):
    guest_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    rsvp_status: str = "Pending"

    @field_validator('rsvp_status')
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in VALID_RSVP_STATUS:
            raise ValueError(f'RSVP status must be one of: {", ".join(VALID_RSVP_STATUS)}')
        return v


class GuestUpdate(BaseModel):
    guest_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    rsvp_status: Optional[str] = None

    @field_validator('rsvp_status')
    @classmethod
    def status_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_RSVP_STATUS:
            raise ValueError(f'RSVP status must be one of: {", ".join(VALID_RSVP_STATUS)}')
        return v


class GuestResponse(BaseModel):
    id: int
    user_id: int
    guest_name: str
    email: Optional[str]
    rsvp_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Admin Schemas ============
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = None

    @field_validator('role')
    @classmethod
    def role_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_ROLES:
            raise ValueError(f'Role must be one of: {", ".join(VALID_ROLES)}')
        return v


class MembershipUpdate(BaseModel):
    membership_status: str

    @field_validator('membership_status')
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in VALID_MEMBERSHIP_STATUS:
            raise ValueError(f'Status must be one of: {", ".join(VALID_MEMBERSHIP_STATUS)}')
        return v
