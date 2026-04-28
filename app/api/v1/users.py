from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from app.db.database import get_db
from app.schemas.user import UserResponse, UserUpdate, MessageResponse
from app.services import user_service
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's profile."""
    return user_service.get_user_by_id(db, uuid.UUID(user_id))


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's profile."""
    return user_service.update_user(db, uuid.UUID(user_id), update_data)


@router.get("/validate", response_model=UserResponse)
def validate_token(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Token validation endpoint used by Stream Service (internal).
    Returns user data if the token is valid.
    """
    return user_service.get_user_by_id(db, uuid.UUID(user_id))


@router.get("/{username}", response_model=UserResponse)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    """Get a public user profile by username."""
    user = user_service.get_user_by_username(db, username)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/me", response_model=MessageResponse)
def deactivate_account(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Deactivate the authenticated user's account."""
    user_service.deactivate_user(db, uuid.UUID(user_id))
    return {"message": "Account deactivated successfully"}
