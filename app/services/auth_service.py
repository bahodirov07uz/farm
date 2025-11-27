from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, data: RegisterRequest) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        hashed_password = get_password_hash(data.password)
        user = await self.user_repo.create(
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def authenticate(self, data: LoginRequest) -> tuple[str, str]:
        user = await self.user_repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        return access, refresh

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repo.get_by_id(user_id)


