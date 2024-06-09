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
    name: str = "group_name"


class UpdateGroupUserModel(BaseModel):
    group_id: int = 1
    type: str = "LEADER"
