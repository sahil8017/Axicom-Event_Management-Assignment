from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import User, Vendor, Item, Order
from schemas import (
    ItemCreate, ItemUpdate, ItemResponse, OrderResponse, OrderStatusUpdate
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/vendor", tags=["Vendor"])


def get_current_vendor(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Vendor:
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Vendor access required")
    
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        # Auto-create vendor profile for users with vendor role but missing profile
        vendor = Vendor(
            user_id=current_user.id,
            company_name=f"{current_user.name}'s Company",
            membership_status="active"
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
    
    return vendor


# ============ Item Management ============
@router.get("/items", response_model=List[ItemResponse])
def list_items(vendor: Vendor = Depends(get_current_vendor), db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.vendor_id == vendor.id).all()
    return items


@router.post("/items", response_model=ItemResponse)
def create_item(data: ItemCreate, vendor: Vendor = Depends(get_current_vendor), db: Session = Depends(get_db)):
    item = Item(
        vendor_id=vendor.id,
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,  # Category is now on item, not vendor
        status="pending"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, data: ItemUpdate, vendor: Vendor = Depends(get_current_vendor), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.vendor_id == vendor.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if data.name:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.price:
        item.price = data.price
    if data.status:
        item.status = data.status
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
def delete_item(item_id: int, vendor: Vendor = Depends(get_current_vendor), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.vendor_id == vendor.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}


# ============ User Requests / Orders ============
@router.get("/requests", response_model=List[OrderResponse])
def list_requests(vendor: Vendor = Depends(get_current_vendor), db: Session = Depends(get_db)):
    orders = db.query(Order).options(joinedload(Order.order_items)).filter(Order.vendor_id == vendor.id).all()
    return orders


@router.put("/requests/{order_id}", response_model=OrderResponse)
def update_request_status(order_id: int, data: OrderStatusUpdate, vendor: Vendor = Depends(get_current_vendor), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.vendor_id == vendor.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.order_status = data.order_status
    db.commit()
    db.refresh(order)
    return order


# ============ Vendor Profile ============
@router.get("/profile")
def get_vendor_profile(vendor: Vendor = Depends(get_current_vendor), current_user: User = Depends(get_current_user)):
    return {
        "id": vendor.id,
        "user_id": vendor.user_id,
        "company_name": vendor.company_name,
        "membership_status": vendor.membership_status,
        "user_name": current_user.name,
        "user_email": current_user.email
    }
