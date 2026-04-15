from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlmodel import Field, SQLModel, create_engine, Session

sqllite_file = "database.db"
sqllite_url = f"sqlite:///{sqllite_file}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqllite_url, connect_args=connect_args)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(application: FastAPI):
    print("Запускаем")
    create_db_and_tables()
    yield
    print("Выгружаем")


app = FastAPI(lifespan=lifespan)


def get_session() -> Session:
    print("Открыли сессию")
    with Session(engine) as session:
        yield session
    print("Закрыли сессию")


@app.get("/")
async def root():
    return {"message": "Поехали!"}


@app.post("/users", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
