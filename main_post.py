from fastapi import Depends, FastAPI
from sqlmodel import create_engine, SQLModel, Field, Session
from contextlib import asynccontextmanager


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


db_name = "База данных"
db_url = f"sqlite:///{db_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(db_url, connect_args=connect_args)


def create_db_and_table() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(application: FastAPI):
    create_db_and_table()
    yield


def get_session() -> Session:
    with Session(engine) as s:
        yield s


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index():
    return {"message": "Поехали!"}


@app.post("/user", response_model=User)
def create_user(user: User, session=Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
