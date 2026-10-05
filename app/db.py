"""SQLite 연결."""
from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    """data/ 폴더에 SQLite 파일을 만들고 테이블을 생성한다."""
    data_dir = get_settings().data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{data_dir / 'scene.db'}", connect_args={"check_same_thread": False}
    )
    from app import models  # noqa: F401  (테이블 등록)

    Base.metadata.create_all(engine)
    return engine


def get_db() -> Iterator[Session]:
    """요청마다 세션을 열고 닫는 FastAPI 의존성."""
    with sessionmaker(bind=get_engine())() as session:
        yield session
