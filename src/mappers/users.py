from src.models import User, UserRead


def user_to_read(user: User) -> UserRead:
    return UserRead.model_validate(user)
