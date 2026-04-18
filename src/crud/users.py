from sqlmodel import Session, select

from src.models import User, UserCreate, UserUpdate
from src.exceptions import UserNotFoundError, UserAlreadyExistsError


def get_users(session: Session) -> list[User]:
    statement = select(User)
    return session.exec(statement).all()


def get_user(user_id: int, session: Session) -> User:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise UserNotFoundError()
    return user


def create_user(name: str, session: Session) -> User:
    statement = select(User).where(User.name == name)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise UserAlreadyExistsError()
    user = User(name=name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def patch_user(user_id: int, user_in: UserUpdate, session: Session) -> User:
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError()

    changes = user_in.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(user_id: int, user_in: UserCreate, session: Session) -> User:
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError()

    user.name = user_in.name

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(user_id: int, session: Session) -> None:
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError()

    session.delete(user)
    session.commit()
