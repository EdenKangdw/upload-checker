from datetime import datetime, timedelta
from database.conn import engineconn, db
from database.schema import User, Channel, Check, UserChannel
from sqlalchemy import cast, Date
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


def get_users(session):
    try:
        return session.query(User).all()
    except Exception as e:
        print(e)
        return None


def add_user(session, user):
    try:
        session.add(user)
        session.commit()

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
    except Exception as e:
        print(e)
        session.rollback()
        return None


def get_user_channels(session: Session, user_id):
    try:
        return session.query(UserChannel).filter(UserChannel.user_id == user_id).all()
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
        print(e)
        session.rollback()
        return None


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


async def get_channel(session, channel_id):
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
        None


################################################################
# check
################################################################


def add_check(session, check):
    session.add(check)
    session.commit()
    return None
    # try:
    #     current_datetime_str = datetime.now().strftime("%Y-%m-%d")
    #     check = (
    #         session.query(Check)
    #         .filter(Check.check_channel_id == check.check_channel_id)
    #         .filter(Check.check_user_id == check.check_user_id)
    #         .filter(cast(Check.created_at, Date) == current_datetime_str)
    #     )
    #     # 중복이 아닌 경우에만 출석체크
    #     if not check:
    #         session.add(check)
    #         session.commit()
    # except Exception as e:
    #     print(e)
    #     session.rollback()
    #     return None


def get_check(session, user_id, channel_id, created_at=None):
    try:
        if created_at:
            data = (
                session.query(Check)
                .filter(Check.check_user_id == user_id)
                .filter(Check.check_channel_id == channel_id)
                .filter(cast(Check.created_at, Date) == created_at)
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
        print(e)
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
            .filter(Check.created_at.between(start_date, end_date))
            .all()
        )
        return data
    except Exception as e:
        print(e)
        return None
