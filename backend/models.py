from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VENDOR = "vendor"
    USER = "user"


class VendorCategory(str, enum.Enum):
    CATERING = "Catering"
    FLORIST = "Florist"
    DECORATION = "Decoration"
    LIGHTING = "Lighting"


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class ProductStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class OrderStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class RSVPStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    DECLINED = "Declined"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    guest_list = relationship("GuestList", back_populates="user")


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    membership_status = Column(String(20), default=MembershipStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="vendor")
    items = relationship("Item", back_populates="vendor")
    orders = relationship("Order", back_populates="vendor")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    status = Column(String(20), default=ProductStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="items")
    cart_items = relationship("CartItem", back_populates="item")
    order_items = relationship("OrderItem", back_populates="item")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String(20), default=PaymentStatus.PENDING.value)
    order_status = Column(String(20), default=OrderStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="orders")
    vendor = relationship("Vendor", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, default=1)

    # Relationships
    user = relationship("User", back_populates="cart_items")
    item = relationship("Item", back_populates="cart_items")


class GuestList(Base):
    __tablename__ = "guest_lists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    guest_name = Column(String(100), nullable=False)
    email = Column(String(100))
    rsvp_status = Column(String(20), default=RSVPStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="guest_list")
