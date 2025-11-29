from collections.abc import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db import get_session
from app.models import User, UserRole
from app.repositories.user import UserRepository
from app.services.auth_service import AuthService
from app.services.branch_service import BranchService
from app.services.drug_service import DrugService
from app.services.inventory_service import InventoryService
from app.services.pharmacy_service import PharmacyService
from app.services.orders import OrderService
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


async def get_db_session() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(session)




async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except Exception as exc:  # noqa: BLE001
        raise credentials_exception from exc

    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await user_repo.get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user

async def get_current_cashier(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify current user is a cashier or superadmin/operator
    """
    if current_user.role not in [UserRole.CASHIER, UserRole.SUPERADMIN, UserRole.OPERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only cashiers can access this endpoint"
        )
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify current user is a superadmin or operator
    """
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.OPERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this endpoint"
        )
    return current_user

def require_roles(*allowed_roles: Iterable[UserRole] | UserRole):
    flattened_roles: set[UserRole] = set()

    def _flatten(item: Iterable[UserRole] | UserRole) -> None:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes, UserRole)):
            for nested in item:
                _flatten(nested)
        else:
            flattened_roles.add(item)  # type: ignore[arg-type]

    for role in allowed_roles:
        _flatten(role)

    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in flattened_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency


allow_superadmin = require_roles(UserRole.SUPERADMIN)
allow_operator = require_roles(UserRole.OPERATOR)
allow_pharmacy_admin = require_roles(UserRole.PHARMACY_ADMIN)
allow_branch_admin = require_roles(UserRole.BRANCH_ADMIN)
allow_cashier = require_roles(UserRole.CASHIER)
allow_branch_admin_or_cashier = require_roles({UserRole.BRANCH_ADMIN, UserRole.CASHIER})
allow_all_users = require_roles(UserRole.USER,UserRole.BRANCH_ADMIN,UserRole.PHARMACY_ADMIN,UserRole.SUPERADMIN,UserRole.CASHIER,UserRole.OPERATOR)

async def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(session)


async def get_pharmacy_service(session: AsyncSession = Depends(get_db_session)) -> PharmacyService:
    return PharmacyService(session)


async def get_branch_service(session: AsyncSession = Depends(get_db_session)) -> BranchService:
    return BranchService(session)


async def get_drug_service(session: AsyncSession = Depends(get_db_session)) -> DrugService:
    return DrugService(session)


async def get_inventory_service(session: AsyncSession = Depends(get_db_session)) -> InventoryService:
    return InventoryService(session)

async def get_order_service(
    session: AsyncSession = Depends(get_db_session)
) -> OrderService:
    return OrderService(session)


async def get_drug_variant_service(
    session: AsyncSession = Depends(get_db_session)
) -> "DrugVariantService":
    from app.services.drug_variant_service import DrugVariantService
    return DrugVariantService(session)