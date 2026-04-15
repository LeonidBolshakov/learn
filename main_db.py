from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlmodel import Field, SQLModel, create_engine, Session

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(application: FastAPI):
    print("startup")
    create_db_and_tables()
    yield
    print("shutdown")


app = FastAPI(lifespan=lifespan)


def get_session():
    print("open session")
    with Session(engine) as session:
        yield session
    print("close session")


@app.get("/")
def root(session: Session = Depends(get_session)):
    print("root")
    return {"message": "Hello World"}
    return {
        "message": "db ready",
        "session_type": str(type(session)),
    }
