"""
Categories API router.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import Category
from schemas import CategoryResponse, CategoryTreeResponse

router = APIRouter()


@router.get("", response_model=CategoryTreeResponse)
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all categories in a tree structure."""
    # Get root categories (level 0)
    result = await db.execute(
        select(Category)
        .where(Category.level == 0)
        .order_by(Category.name)
    )
    root_categories = result.scalars().all()
    
    # Build tree structure
    def build_tree(parent_id=None):
        query = select(Category).order_by(Category.name)
        if parent_id is None:
            query = query.where(Category.level == 0)
        else:
            query = query.where(Category.parent_id == parent_id)
        
        result = await db.execute(query)
        categories = result.scalars().all()
        
        tree = []
        for cat in categories:
            cat_dict = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "category_path": cat.category_path,
                "level": cat.level,
                "parent_id": cat.parent_id,
                "children": build_tree(cat.id),
            }
            tree.append(cat_dict)
        return tree
    
    categories_tree = build_tree()
    return CategoryTreeResponse(categories=categories_tree)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific category by ID."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category
