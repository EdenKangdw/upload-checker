from datetime import datetime, timedelta
from io import BytesIO
from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer
from api_model.model import ChannelModel
from sqlalchemy.orm import Session
from util.check import kor_week_day, prayer_check_dates
from database.query import (
    add_channel,
    add_user_channel,
    get_channel,
    get_channel_check_download,
    get_channel_checks,
    get_channel_group_checks,
    get_channel_group_user,
    get_channel_with_code,
    get_channel_with_name,
    get_group_users,
    get_user_channel_info,
    update_group_user,
)
from database.schema import Channel, GroupUser, UserChannel
from util.auth import get_current_user
from database.conn import db
import pandas as pd

oauth2_scheme = HTTPBearer()
app = APIRouter()


@app.post("", status_code=200)
async def post_channel_api(
    params: ChannelModel,
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    생성하고자 하는 채널의 정보를 받아 채널을 생성하고, 만들어진 채널의 정보를 return 합니다.
    """
    input = params.dict()

    # check user
    user = await get_current_user(token)

    # create channel
    channel = Channel(
        channel_name=input.get("name"),
        channel_code=input.get("code"),
        channel_creator_id=user.user_id,
        channel_check_type=input.get("check_type"),
    )
    add_channel_result = add_channel(session, channel)
    if not add_channel_result:
        return JSONResponse(
            {"error": "이미 존재하는 code 입니다. 다른 code를 사용해주세요"},
            status_code=500,
        )

    # add user channel
    user_channel = UserChannel(
        user_id=user.user_id,
        channel_id=channel.channel_id,
        user_type="CREATOR",
    )
    add_user_channel(session, user_channel)
    if not add_user_channel:
        return JSONResponse({"error": "Can't add user channel"}, status_code=500)

    # get channel
    channel_result = await get_channel_with_name(
        session, creator_id=user.user_id, channel_name=channel.channel_name
    )
    return channel_result


@app.get("/user", status_code=200)
async def get_channel_user(
    channel_id: int = Query(default=0),
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
):
    """
    채널 내 유저 정보를 return 합니다.
    - isManager : 채널 매니저 여부
    - isCreator : 채널 생성자 여부
    - group : 채널 유저 소속 그룹 정보
    """
    # user check
    user = await get_current_user(token)

    # get channel users
    channel_user = get_user_channel_info(session, channel_id, user.user_id)
    if not channel_user:
        return JSONResponse({"error": "Can't get channel user"}, status_code=500)

    # set user type option
    result = {
        "user_id": user.user_id,
        "channel_id": channel_id,
        "isManager": False,
        "isCreator": False,
    }

    # 유저 group 정보 추출
    channel_group_user = get_channel_group_user(session, user.user_id, channel_id)
    if channel_group_user:
        group_user: GroupUser = channel_group_user["group_user"]
        group_name = channel_group_user["group_name"]
        group = {"id": group_user.group_id, "name": group_name, "type": group_user.type}
        result.update({"group": group})

    result["isManager"] = (
        True if channel_user.user_type in ["MANAGER", "CREATOR"] else False
    )
    result["isCreator"] = True if channel_user.user_type == "CREATOR" else False
    return result


@app.get("/user/type", status_code=200)
async def get_channel_user(
    channel_id: int = Query(default=0),
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
):
    """
    선택할 수 있는 채널 내 유저 타입 목록을 return 합니다.
    """
    # user check
    user = await get_current_user(token)

    result = [
        {"type": "MANAGER", "name": "관리자"},
        {"type": "MEMBER", "name": "멤버"},
    ]
    return result


@app.post("/user", status_code=200)
async def post_channel_user_api(
    channel_id: int = Body(..., description="채널 아이디"),
    user_id: int = Body(..., description="유저 아이디"),
    type: str = Body(..., description="유저 타입(MANAGER, MEMBER)"),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 내 유저 정보를 업데이트 합니다.
    - MEMBER : 일반 유저
    - MANAGER : 매니저
    """
    # user check
    user = await get_current_user(token)

    # check is creator
    user_channel = get_user_channel_info(session, channel_id, user.user_id)
    if not user_channel:
        return JSONResponse({"error": "Can't get channel user"}, status_code=500)
    if user_channel.user_type != "CREATOR":
        return JSONResponse({"error": "You are not creator"}, status_code=500)

    # update group user
    update_group_user_result = update_group_user(
        session, channel_id, user.user_id, type
    )
    if not update_group_user_result:
        return JSONResponse({"error": "can't update group_user"}, status_code=500)

    return True


@app.get("/check", status_code=200)
async def get_check_channel_api(
    channel_id: int = Query(default=0),
    start_date=Query(default="", description="체크기준 시작날짜(KST)"),
    end_date=Query(default="", description="체크기준 종료날짜(KST)"),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널의 생성자가 사용합니다. 채널 내, 일정 기간동안 체크한 사람의 목록을 확인힐 수 있습니다.
    - is_manager : True 인 경우만 사용합니다.
    """

    # check user
    user = await get_current_user(token)
    print("user: %s" % user.user_id)

    # TODO: check user's permissions :  - 나중에 변경될 예정
    user_channel = get_user_channel_info(session, channel_id, user.user_id)
    if user_channel.user_type == "MEMBER":
        return JSONResponse({"error": "유저 권한 없음"}, status_code=500)

    # get period
    end_date = start_date if end_date == "" else end_date
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    # TODO : 기도회 기간으로 기간제한
    prayer_start_date = datetime.strptime("2024-06-08", "%Y-%m-%d")
    prayer_end_date = datetime.strptime("2024-07-13", "%Y-%m-%d")
    if start_datetime < prayer_start_date:
        start_datetime = prayer_start_date
    if end_datetime > prayer_end_date:
        prayer_end_date

    period_array = [
        start_datetime + timedelta(days=x)
        for x in range((end_datetime - start_datetime).days + 1)
    ]

    # get user's group
    user_group_list = get_group_users(session, user.user_id)
    permission_group_list = list(filter(lambda x: x.type != "MEMBER", user_group_list))
    if not permission_group_list:
        return JSONResponse({"error": "유저 권한 없음"}, status_code=500)
    permission_group_ids = [x.group_id for x in permission_group_list]

    # get checks
    channel_check_list = []
    # print(period_array)
    for target_datetime in period_array:
        current_date_str = target_datetime.strftime("%Y-%m-%d")
        if current_date_str in prayer_check_dates():
            week_day = kor_week_day(target_datetime)
            if permission_group_ids:
                checks = get_channel_group_checks(
                    session, channel_id, current_date_str, permission_group_ids
                )
            else:
                checks = get_channel_checks(session, channel_id, current_date_str)

            datetime_checks = list(
                map(
                    lambda x: x.user_nickname if x.user_nickname else x.user_name,
                    checks,
                )
            )
            check = {
                "date": f"{current_date_str}({week_day})",
                "checks": datetime_checks,
            }
            channel_check_list.append(check)
            print("checks: %s" % datetime_checks)

    return channel_check_list


@app.post("/join")
async def post_channel_join(
    channel_code: str = Body(..., description="채널 코드"),
    dummy: str = Body(description="body 만들기용 데이터", default=None),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 코드를 통해 채널 정보를 받은 후, 채널에 가입합니다.
    """

    # user check
    user = await get_current_user(token)

    # get channel with code
    channel = await get_channel_with_code(session, channel_code)
    if not channel:
        return JSONResponse(
            {"error": "채널코드에 해당하는 채널을 찾을 수 없습니다"},
            status_code=500,
        )
    user_channel = UserChannel(user_id=user.user_id, channel_id=channel.channel_id)

    # join channel
    # check if user is already in channel
    selected_user_channel = get_user_channel_info(
        session, channel.channel_id, user.user_id
    )
    if not selected_user_channel:
        add_user_channel(session, user_channel)

    return dict(channel=channel)


@app.get("")
async def get_channel_api(
    channel_id: int = Query(description="채널 아이디", default=1),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 아이디를 통해 채널 정보를 얻습니다. 채널 입장에 사용합니다.
    """
    # user check
    user = await get_current_user(token)

    # get channel with code
    channel = await get_channel(session, channel_id)

    return dict(channel=channel)


@app.get("/check/download")
async def download_channel_check(
    channel_id: int = Query(description="채널 아이디", default=1),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    # user check
    user = await get_current_user(token)

    # get check list
    channel_checks = get_channel_check_download(session, channel_id)

    # get prayer date list
    prayer_check_date_list = prayer_check_dates()

    # 데이터를 데이터프레임으로 변환 - 개인별 데이터
    data = {}
    for check in channel_checks:
        user_name = check.user_nickname if check.user_nickname else check.user_name
        if user_name not in data:
            data[user_name] = {"group_name": check.group_name}
        check_date_str = check.checked_at.strftime("%Y-%m-%d")
        if not data[user_name].get(check_date_str):
            if check_date_str in prayer_check_date_list:
                for date in prayer_check_date_list:
                    data[user_name][date] = "X"  # 기본값은 'X'
        if check_date_str in prayer_check_date_list:
            data[user_name][check_date_str] = "O"

    df_data = []
    for user_name, values in data.items():
        row = {"이름": user_name, "팀": values["group_name"]}
        row.update({date: values[date] for date in prayer_check_date_list})
        df_data.append(row)

    df = pd.DataFrame(df_data)
    df = df.sort_values(by="이름", ascending=True)

    # 데이터를 데이터프레임으로 변환 - 그룹별 데이터
    team_data = {}
    for check in channel_checks:
        if check.group_name not in team_data:
            team_data[check.group_name] = {}
        check_date_str = check.checked_at.strftime("%Y-%m-%d")
        if check_date_str not in team_data[check.group_name]:
            if check_date_str in prayer_check_date_list:
                for date in prayer_check_date_list:
                    team_data[check.group_name][date] = 0
        if check_date_str in prayer_check_date_list:
            team_data[check.group_name][check_date_str] += 1
    print(team_data)

    df_group_data = []
    for group_name, values in team_data.items():
        row = {"팀": group_name}
        row.update({date: values[date] for date in prayer_check_date_list})
        df_group_data.append(row)

    df_g = pd.DataFrame(df_group_data)
    df_g = df_g.sort_values(by="팀", ascending=True)

    # 엑셀 파일로 변환
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="개인별 현황")
        df_g.to_excel(writer, index=False, sheet_name="팀별 현황")
    buffer.seek(0)

    # UTF-8로 파일 이름 인코딩
    filename = "check_result.xlsx"
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename.encode('utf-8').decode('latin-1')}"
    }

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
