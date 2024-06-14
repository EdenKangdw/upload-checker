from datetime import datetime, time, timedelta
import traceback

from fastapi import logger
from database.conn import engineconn, db
from database.schema import Group, GroupUser, User, Channel, Check, UserChannel
from sqlalchemy import cast, Date, desc
from sqlalchemy.orm import Session


################################################################
# user
################################################################
def get_user(session: Session, username):
    try:
        return session.query(User).filter(User.user_name == username).first()
    except Exception as e:
        print(e)
        return None


def get_user_with_id(session: Session, user_id):
    try:
        return session.query(User).filter(User.user_id == user_id).first()
    except Exception as e:
        print(e)
        return None


def get_users(session: Session):
    try:
        return session.query(User).all()
    except Exception as e:
        print(e)
        return None


def add_user(session: Session, user):
    try:
        session.add(user)
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        return None


def update_user_nickname(session: Session, user_id, user_nickname):

    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.user_nickname = user_nickname
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        return None


################################################################
# Group
################################################################


def add_group(session: Session, group):
    try:
        session.add(group)
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        return None


def get_groups(session: Session):
    try:
        return session.query(Group).all()
    except Exception as e:
        print(e)
        return None


################################################################
# GroupUser
################################################################


def get_group_users(session: Session, user_id):
    try:
        return session.query(GroupUser).filter(User.user_id == user_id).all()
    except Exception as e:
        print(e)
        return None


def add_group_user(session: Session, group_user):
    try:
        checked_group_user = (
            session.query(GroupUser)
            .filter(GroupUser.user_id == group_user.user_id)
            .filter(GroupUser.group_id == group_user.group_id)
            .first()
        )
        # 중복이 아닐 경우만
        if not checked_group_user:
            session.add(group_user)
            session.commit()
            return True
    except Exception as e:
        print(e)
        session.rollback()
        return None
    return False


def update_group_user(session: Session, user_id, group_id, user_type: str):
    try:
        group_user = (
            session.query(GroupUser)
            .filter(GroupUser.user_id == user_id)
            .filter(GroupUser.group_id == group_id)
            .first()
        )
        group_user.type = user_type
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        return None


################################################################
# user-channel
################################################################


def add_user_channel(session, user_channel):
    try:
        session.add(user_channel)
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        return None


def get_user_channels(session: Session, user_id):
    try:
        result = (
            session.query(Channel, UserChannel.user_type)
            .join(Channel, Channel.channel_id == UserChannel.channel_id)
            .filter(UserChannel.user_id == user_id)
            .all()
        )
        user_channels = []
        for channel, user_type in result:
            user_channels.append(
                {
                    "channel_id": channel.channel_id,
                    "channel_name": channel.channel_name,
                    "user_type": user_type,
                }
            )
        return user_channels

    except Exception as e:
        print(e)
        return None


def get_user_channel_info(session: Session, channel_id, user_id) -> UserChannel:
    try:
        return (
            session.query(UserChannel)
            .filter(UserChannel.user_id == user_id)
            .filter(UserChannel.channel_id == channel_id)
            .first()
        )
    except Exception as e:
        print(e)
        return None


################################################################
# channel
################################################################
def add_channel(session, channel):
    try:
        session.add(channel)
        session.commit()
    except Exception as e:
        print("Error adding channel : " + str(e))
        session.rollback()
        return None
    return True


async def get_channel_with_name(session, creator_id, channel_name):
    try:
        data = (
            session.query(Channel)
            .filter(Channel.channel_creator_id == creator_id)
            .filter(Channel.channel_name == channel_name)
            .first()
        )
        return data

    except Exception as e:
        print(e)
        None


async def get_channel(session, channel_id) -> Channel:
    try:
        data = session.query(Channel).filter(Channel.channel_id == channel_id).first()
        return data

    except Exception as e:
        print(e)
        None


async def get_channel_with_code(session, channel_code):
    try:
        data = (
            session.query(Channel).filter(Channel.channel_code == channel_code).first()
        )
        return data

    except Exception as e:
        print(e)
        return None


################################################################
# check
################################################################


def add_check(session, check: Check):
    try:
        target_date_time: datetime = check.checked_at
        target_date_time_str: str = datetime.strftime(target_date_time, "%Y-%m-%d")
        current_check = (
            session.query(Check)
            .filter(Check.check_channel_id == check.check_channel_id)
            .filter(Check.check_user_id == check.check_user_id)
            .filter(cast(Check.checked_at, Date) == target_date_time_str)
            .first()
        )
        # 중복이 아닌 경우에만 출석체크
        if not current_check:
            session.add(check)
            session.commit()
        return check
    except Exception as e:
        print(e)
        session.rollback()
        return None
    return False


def get_check(session, user_id, channel_id, checked_at=None):
    try:
        if checked_at:
            data = (
                session.query(Check)
                .filter(Check.check_user_id == user_id)
                .filter(Check.check_channel_id == channel_id)
                .filter(cast(Check.checked_at, Date) == cast(checked_at, Date))
                .first()
            )
            return data
        return (
            session.query(Check)
            .filter(Check.check_user_id == user_id)
            .filter(Check.check_channel_id == channel_id)
            .first()
        )

    except Exception as e:
        traceback.print_exc(e)
        return None


def get_period_check(session, user_id, channel_id, check_start_time, check_end_time):
    try:
        data = (
            session.query(Check)
            .filter(Check.check_user_id == user_id)
            .filter(Check.check_channel_id == channel_id)
            .filter(Check.checked_at.between(check_start_time, check_end_time))
            .order_by(desc(Check.checked_at))
            .first()
        )
        return data

    except Exception as e:
        traceback.print_exc()
        return None


def get_channel_checks(session, channel_id: int, created_at=None) -> User:
    try:
        if created_at is not None:
            data = (
                session.query(Check.check_user_id, User.user_name)
                .join(User, Check.check_user_id == User.user_id)
                .filter(Check.check_channel_id == channel_id)
                .filter(cast(Check.created_at, Date) == created_at)
                .group_by(Check.check_user_id)
                .all()
            )
            return data
        return (
            session.query(Check.check_user_id, User.user_name)
            .join(User, Check.check_user_id == User.user_id)
            .filter(Check.check_channel_id == channel_id)
            .group_by(Check.check_user_id)
            .all()
        )
    except Exception as e:
        print(e)
        return None


def get_user_checks_channel(
    session, channel_id, user_id, start_date_str, end_date_str
) -> Check:
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)

        data = (
            session.query(Check)
            .filter(Check.check_channel_id == channel_id)
            .filter(Check.check_user_id == user_id)
            .filter(Check.checked_at.between(start_date, end_date))
            .all()
        )
        return data
    except Exception as e:
        print(e)
        return None
