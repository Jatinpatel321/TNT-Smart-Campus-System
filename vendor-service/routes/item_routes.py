from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Menu, Item
from schemas import ItemCreate, ItemResponse
from security import verify_vendor_token
from api.deps.vendor import get_current_vendor


# 🔐 ROUTER-LEVEL SECURITY (APPLIED ONCE)
router = APIRouter(
    prefix="/items",
    tags=["Items"],
    dependencies=[Depends(verify_vendor_token)]
)


# --------------------------------------------------
# CREATE ITEM (menu → vendor ownership enforced)
# --------------------------------------------------
@router.post("/", response_model=ItemResponse)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    # Verify menu belongs to current vendor
    menu = (
        db.query(Menu)
        .filter(
            Menu.id == item.menu_id,
            Menu.vendor_id == current_vendor.id
        )
        .first()
    )

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found or access denied"
        )

    new_item = Item(
        name=item.name,
        price=item.price,
        description=item.description,
        menu_id=menu.id
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# --------------------------------------------------
# GET ITEMS OF A MENU (vendor scoped)
# --------------------------------------------------
@router.get("/menu/{menu_id}", response_model=list[ItemResponse])
def get_menu_items(
    menu_id: int,
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    # Verify menu belongs to vendor
    menu = (
        db.query(Menu)
        .filter(
            Menu.id == menu_id,
            Menu.vendor_id == current_vendor.id
        )
        .first()
    )

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found or access denied"
        )

    return db.query(Item).filter(Item.menu_id == menu.id).all()
