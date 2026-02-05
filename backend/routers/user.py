from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import User, Vendor, Item, Order, OrderItem, CartItem, GuestList
from schemas import (
    VendorResponse, ItemResponse, 
    CartItemCreate, CartItemResponse,
    OrderCreate, OrderResponse, 
    GuestCreate, GuestUpdate, GuestResponse
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])


def require_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(status_code=403, detail="User access required")
    return current_user


# ============ Browse Vendors ============
@router.get("/vendors", response_model=List[VendorResponse])
def list_vendors(db: Session = Depends(get_db), user: User = Depends(require_user)):
    """List all active vendors"""
    return db.query(Vendor).filter(Vendor.membership_status == "active").all()


@router.get("/vendors/{vendor_id}/items", response_model=List[ItemResponse])
def get_vendor_items(vendor_id: int, category: str = None, db: Session = Depends(get_db), user: User = Depends(require_user)):
    """Get approved items from a vendor, optionally filtered by category"""
    query = db.query(Item).filter(Item.vendor_id == vendor_id, Item.status == "approved")
    if category:
        query = query.filter(Item.category == category)
    return query.all()


# ============ Browse All Items ============
@router.get("/items", response_model=List[ItemResponse])
def list_all_items(category: str = None, db: Session = Depends(get_db), user: User = Depends(require_user)):
    """List all approved items from active vendors, optionally filtered by PRODUCT category"""
    query = db.query(Item).join(Vendor).filter(
        Item.status == "approved",
        Vendor.membership_status == "active"
    )
    if category:
        query = query.filter(Item.category == category)  # Filter by Item category now
    return query.all()


# ============ Cart Management ============
@router.get("/cart", response_model=List[CartItemResponse])
def get_cart(db: Session = Depends(get_db), user: User = Depends(require_user)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    result = []
    for ci in cart_items:
        item = db.query(Item).filter(Item.id == ci.item_id).first()
        result.append({
            "id": ci.id,
            "item_id": ci.item_id,
            "quantity": ci.quantity,
            "item": item
        })
    return result


@router.post("/cart", response_model=CartItemResponse)
def add_to_cart(data: CartItemCreate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    # Check if item exists
    item = db.query(Item).filter(Item.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.user_id == user.id, 
        CartItem.item_id == data.item_id
    ).first()
    
    if existing:
        existing.quantity += data.quantity
        db.commit()
        db.refresh(existing)
        return {"id": existing.id, "item_id": existing.item_id, "quantity": existing.quantity, "item": item}
    
    cart_item = CartItem(
        user_id=user.id,
        item_id=data.item_id,
        quantity=data.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return {"id": cart_item.id, "item_id": cart_item.item_id, "quantity": cart_item.quantity, "item": item}


@router.delete("/cart/{cart_item_id}")
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/cart")
def clear_cart(db: Session = Depends(get_db), user: User = Depends(require_user)):
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}


# ============ Orders ============
@router.get("/orders", response_model=List[OrderResponse])
def list_orders(db: Session = Depends(get_db), user: User = Depends(require_user)):
    orders = db.query(Order).options(joinedload(Order.order_items)).filter(Order.user_id == user.id).all()
    return orders


@router.post("/orders", response_model=OrderResponse)
def create_order(data: OrderCreate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    # Calculate total
    total = 0
    items_data = []
    for item_data in data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
        total += item.price * item_data.quantity
        items_data.append((item, item_data.quantity))
    
    # Create order
    order = Order(
        user_id=user.id,
        vendor_id=data.vendor_id,
        total_amount=total,
        payment_status="pending",
        order_status="Pending",
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        address=data.address,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
        payment_method=data.payment_method
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    for item, qty in items_data:
        order_item = OrderItem(
            order_id=order.id,
            item_id=item.id,
            quantity=qty,
            price=item.price
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    return order


@router.put("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.order_status != "Pending":
        raise HTTPException(status_code=400, detail="Cannot cancel non-pending order")
    
    order.order_status = "Cancelled"
    db.commit()
    db.refresh(order)
    return order


@router.put("/orders/{order_id}/pay", response_model=OrderResponse)
def pay_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.payment_status = "completed"
    db.commit()
    db.refresh(order)
    return order


# ============ Guest List ============
@router.get("/guests", response_model=List[GuestResponse])
def list_guests(db: Session = Depends(get_db), user: User = Depends(require_user)):
    guests = db.query(GuestList).filter(GuestList.user_id == user.id).all()
    return guests


@router.post("/guests", response_model=GuestResponse)
def add_guest(data: GuestCreate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    guest = GuestList(
        user_id=user.id,
        guest_name=data.guest_name,
        email=data.email,
        rsvp_status=data.rsvp_status
    )
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest


@router.put("/guests/{guest_id}", response_model=GuestResponse)
def update_guest(guest_id: int, data: GuestUpdate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    guest = db.query(GuestList).filter(GuestList.id == guest_id, GuestList.user_id == user.id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    if data.guest_name:
        guest.guest_name = data.guest_name
    if data.email is not None:
        guest.email = data.email
    if data.rsvp_status:
        guest.rsvp_status = data.rsvp_status
    
    db.commit()
    db.refresh(guest)
    return guest


@router.delete("/guests/{guest_id}")
def delete_guest(guest_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    guest = db.query(GuestList).filter(GuestList.id == guest_id, GuestList.user_id == user.id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    db.delete(guest)
    db.commit()
    return {"message": "Guest deleted successfully"}
