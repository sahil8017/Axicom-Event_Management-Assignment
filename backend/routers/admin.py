from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Vendor, Item
from schemas import (
    UserResponse, UserUpdate, VendorResponse, VendorUpdate, 
    MembershipUpdate, ItemResponse
)
from routers.auth import get_current_user
from auth import get_password_hash

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ============ User Management ============
@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).all()
    return users


@router.post("/users", response_model=UserResponse)
def add_user(data: dict, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing = db.query(User).filter(User.email == data.get("email")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(
        name=data.get("name"),
        email=data.get("email"),
        password_hash=get_password_hash(data.get("password", "password123")),
        role=data.get("role", "user")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email
    if data.role:
        user.role = data.role
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# ============ Vendor Management ============
@router.get("/vendors", response_model=List[VendorResponse])
def list_vendors(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    vendors = db.query(Vendor).all()
    return vendors


@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: int, data: VendorUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    if data.company_name:
        vendor.company_name = data.company_name
    if data.category:
        vendor.category = data.category
    if data.membership_status:
        vendor.membership_status = data.membership_status
    
    db.commit()
    db.refresh(vendor)
    return vendor


# ============ Membership Management ============
@router.put("/memberships/{vendor_id}", response_model=VendorResponse)
def update_membership(vendor_id: int, data: MembershipUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    vendor.membership_status = data.membership_status
    db.commit()
    db.refresh(vendor)
    return vendor


# ============ Product Approval ============
@router.get("/items", response_model=List[ItemResponse])
def list_all_items(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    items = db.query(Item).all()
    return items


@router.put("/items/{item_id}/approve")
def approve_item(item_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.status = "approved"
    db.commit()
    db.refresh(item)
    return {"message": "Item approved successfully", "item": {"id": item.id, "name": item.name, "status": item.status}}


@router.put("/items/{item_id}/reject")
def reject_item(item_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.status = "rejected"
    db.commit()
    db.refresh(item)
    return {"message": "Item rejected", "item": {"id": item.id, "name": item.name, "status": item.status}}


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}
