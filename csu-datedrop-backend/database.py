from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 固定写在 backend 目录，避免从仓库根目录启动 uvicorn 时把库建到别处
_BACKEND_DIR = Path(__file__).resolve().parent
_DB_FILE = _BACKEND_DIR / "datedrop.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_DB_FILE.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
