from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Menu
from schemas import MenuCreate, MenuResponse
from api.deps.vendor import get_current_vendor

# 🔐 PER-ENDPOINT SECURITY
router = APIRouter(
    prefix="/menus",
    tags=["Menus"]
)


@router.post("/", response_model=MenuResponse)
def create_menu(
    menu: MenuCreate,
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    # Create menu for current vendor (ignore any vendor_id in request)
    new_menu = Menu(
        name=menu.name,
        vendor_id=current_vendor.id
    )

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)

    return new_menu


@router.get("/", response_model=list[MenuResponse])
def get_vendor_menus(
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    return db.query(Menu).filter(Menu.vendor_id == current_vendor.id).all()
