from sqlalchemy import func, DateTime, Column, TEXT, INTEGER, BIGINT, String
from database.base import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    user_name = Column(String(30), nullable=False)
    user_nickname = Column(String(30), nullable=True)


class Group(Base):
    __tablename__ = "group"

    group_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    group_name = Column(String(30), nullable=False)


class GroupUser(Base):
    __tablename__ = "group__user"

    id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    group_id = Column(INTEGER, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    type = Column(String(30), nullable=False, default="MEMBER")


class Channel(Base):
    __tablename__ = "channel"

    channel_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    channel_name = Column(String(30), nullable=False)
    channel_code = Column(String(30), nullable=False, unique=True)
    channel_creator_id = Column(INTEGER, nullable=False)
    channel_user_count = Column(INTEGER, nullable=False, default=0)
    channel_check_type = Column(String(10), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp())
    created_at = Column(DateTime, default=func.current_timestamp())


class UserChannel(Base):
    __tablename__ = "user__channel"

    user_channel_id = Column(
        INTEGER, primary_key=True, nullable=False, autoincrement=True
    )
    channel_id = Column(INTEGER, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp())
    created_at = Column(DateTime, default=func.current_timestamp())


class Check(Base):
    __tablename__ = "check"

    check_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    check_channel_id = Column(INTEGER, nullable=False)
    check_user_id = Column(INTEGER, nullable=False)
    checked_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp())
    created_at = Column(DateTime, default=func.current_timestamp())
