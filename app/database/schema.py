from sqlalchemy import Time, func, DateTime, Column, TEXT, INTEGER, BIGINT, String
from database.base import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    user_name = Column(String(30), nullable=False)
    user_nickname = Column(String(30), nullable=True)
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at = Column(DateTime, default=func.current_timestamp())


class Group(Base):
    __tablename__ = "group"

    group_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    group_name = Column(String(30), nullable=False)
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at = Column(DateTime, default=func.current_timestamp())


class GroupUser(Base):
    __tablename__ = "group__user"

    id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    group_id = Column(INTEGER, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    type = Column(String(30), nullable=False, default="MEMBER")
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at = Column(DateTime, default=func.current_timestamp())


class Channel(Base):
    __tablename__ = "channel"

    channel_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    channel_name = Column(String(30), nullable=False)
    channel_code = Column(String(30), nullable=False, unique=True)
    channel_creator_id = Column(INTEGER, nullable=False)
    channel_user_count = Column(INTEGER, nullable=False, default=0)
    channel_check_option_id = Column(INTEGER, nullable=True)
    channel_check_type = Column(String(10), nullable=False)
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at = Column(DateTime, default=func.current_timestamp())


class UserChannel(Base):
    __tablename__ = "user__channel"

    user_channel_id = Column(
        INTEGER, primary_key=True, nullable=False, autoincrement=True
    )
    channel_id = Column(INTEGER, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    user_type = Column(String(30), nullable=False, default="MEMBER")
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at = Column(DateTime, default=func.current_timestamp())


class Check(Base):
    __tablename__ = "check"

    check_id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    check_channel_id = Column(INTEGER, nullable=False)
    check_user_id = Column(INTEGER, nullable=False)
    checked_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at = Column(DateTime, default=func.current_timestamp())


class CheckOption(Base):
    __tablename__ = "check_option"

    id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(30), nullable=False)
    start_date = Column(DateTime, default=func.current_timestamp(), nullable=False)
    end_date = Column(DateTime, default=func.current_timestamp(), nullable=False)
    week_option = Column(String(7), default="1234567", comment="1-7 : 월요일-일요일")
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_by = Column(INTEGER, nullable=False, comment="이벤트 생성자 id")
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at = Column(DateTime, default=func.current_timestamp())
