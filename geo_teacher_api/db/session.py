from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/geo_teacher_api"

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
