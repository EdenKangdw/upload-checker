from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from api_model.model import GroupModel, UpdateGroupUserModel
from sqlalchemy.orm import Session
from database.query import add_group, get_groups, update_group_user
from database.schema import Group
from util.auth import get_current_user
from database.conn import db

oauth2_scheme = HTTPBearer()
app = APIRouter()


@app.post("/")
async def post_group(
    group: GroupModel,
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    그룹을 생성합니다.
    """
    # get user info
    user = await get_current_user(token)

    # add group
    group = Group(
        group_name=group.name,
    )

    # add group user
    added_group = add_group(session, group)
    if not added_group:
        return JSONResponse({"error": "Could not add group"}, status_code=500)

    return added_group


@app.get("/list", status_code=200)
async def get_group_list(
    session: Session = Depends(db.session), token: HTTPBearer = Depends(oauth2_scheme)
):
    """
    전체 팀 목록을 return 합니다.
    """
    # user check
    user = await get_current_user(token)

    # get group list
    group_list = get_groups(session)
    if not group_list:
        return JSONResponse({"error": "cannot get groups"}, status_code=500)

    return group_list


@app.post("/user")
async def post_group_user(
    group_user: UpdateGroupUserModel,
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
):
    """
    팀 내에서 유저 정보를 업데이트 합니다.
    - type : LEADER, MEMBER
    """
    # user check
    user = await get_current_user(token)

    # update group user
    update_group_user_result = update_group_user(
        session, user.user_id, group_user.group_id, group_user.type
    )
    if not update_group_user_result:
        return JSONResponse({"error": "can't update group_user"}, status_code=500)

    return True
