from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_auth_service, get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models import User
from app.schemas import UserRead
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.register(payload)


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    access, refresh = await auth_service.authenticate(payload)
    return Token(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=Token)
async def refresh_token(payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        token_data = decode_token(payload.refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = token_data.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await auth_service.get_user_by_id(int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return Token(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


