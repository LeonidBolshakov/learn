from sqlmodel import Session

from src.crud.users import (
    get_user_by_id,
    get_user_by_name,
    create_user,
    get_users,
    delete_user,
)
from src.models import UserCreate, UserUpdate, User
from src.exceptions import UserNotFoundError, UserAlreadyExistsError


def get_user_service(user_id: int, session: Session):
    return _get_user_or_404(user_id, session)


def _get_user_or_404(user_id: int, session: Session) -> User:
    user = get_user_by_id(user_id, session)
    if user is None:
        raise UserNotFoundError(user_id)
    return user


def create_user_service(user_in: UserCreate, session: Session):
    _ensure_user_name_is_unique(user_in.name, session)

    user = create_user(user_in.name, session)
    return save_user(user, session)


def get_users_service(session: Session):
    return get_users(session)


def update_user_service(user_id: int, user_in: UserCreate, session: Session) -> User:
    user = _get_user_or_404(user_id, session)

    _ensure_user_name_is_unique(user_in.name, session, exclude_user_id=user.id)

    user.name = user_in.name
    return save_user(user, session)


def patch_user_service(
    user_id: int,
    user_in: UserUpdate,
    session: Session,
) -> User:
    user = _get_user_or_404(user_id, session)

    if user_in.name is not None:
        _ensure_user_name_is_unique(
            user_in.name,
            session,
            exclude_user_id=user.id,
        )
        user.name = user_in.name

    return save_user(user, session)


def delete_user_service(user_id: int, session: Session) -> None:
    user = _get_user_or_404(user_id, session)
    delete_user(user, session)


def _ensure_user_name_is_unique(
    name: str,
    session: Session,
    exclude_user_id: int | None = None,
) -> User:
    existing_user = get_user_by_name(name, session)

    if existing_user is None:
        return

    if exclude_user_id is not None and existing_user.id == exclude_user_id:
        return

    raise UserAlreadyExistsError(name)


def save_user(user: User, session: Session) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
