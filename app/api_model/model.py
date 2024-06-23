from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChannelModel(BaseModel):
    name: str = "name"
    code: str = "code"
    check_type: str = "check"


class UpdateUserModel(BaseModel):
    nickname: Optional[str] = "nickname"
    group_id: Optional[int] = None


class GroupModel(BaseModel):
    name: str = "그룹 이름"
    channel_id: int = "0"


class UpdateGroupUserModel(BaseModel):
    group_id: int = 1
    type: str = "LEADER"


class EventModel(BaseModel):
    name: str = "event"
    start_date: str = "YYYY-MM-DD"
    end_date: str = "YYYY-MM-DD"
    start_time: str = "hh:mm"
    end_time: str = "HH:mm"
    week_option: str = "1234567"
