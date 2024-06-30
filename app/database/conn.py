from typing import Callable, Generator
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from config import Config
from database.base import Base

config = Config()


DB_URL = f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}?charset=utf8mb4&collation=utf8mb4_unicode_ci&autocommit=true"


class engineconn:
    def __init__(self):
        # https://tjddnjs.tistory.com/69 - 여기 참고, 비관적 방법 적용
        self.engine = create_engine(DB_URL, pool_pre_ping=True)

    def sessionmaker(self):
        Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn

    def init_db(self):
        Base.metadata.create_all(self.engine)
        print("init database completed")

    def get_db(self) -> Generator:
        db = self.sessionmaker()
        try:
            yield db
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    @property
    def session(self) -> Callable:
        return self.get_db


db = engineconn()
