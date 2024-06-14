from fastapi import Body, Depends, FastAPI, Request
from database.query import *
from database.conn import engineconn, db
from database.base import Base
from database.schema import User, Check
from config import Config
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from util.auth import encode_token
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging

# import router
from route.user import app as user_router
from route.check import app as check_router
from route.channel import app as channel_router
from route.group import app as group_router
from route.oauth import app as oauth_router

oauth2_scheme = HTTPBearer()

# template
templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# db connection

engine = engineconn()
session = engine.sessionmaker()
Base.metadata.create_all(bind=engine.engine)

# get config
config = Config()

# include router
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(check_router, prefix="/check", tags=["Check"])
app.include_router(channel_router, prefix="/channel", tags=["Channel"])
app.include_router(oauth_router, prefix="/oauth", tags=["OAuth"])
app.include_router(group_router, prefix="/group", tags=["Group"])

"""
http://localhost:8000/oauth/kakao/redirect?code=914rIhV3Epl2n9ls6YZL3Kh766OxdsqOe-WQPokOlHqikSB1Neq4URoHYIgKPXRpAAABjMONm8Gxu3fh8M0xkQ
"""


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/dummy/user", status_code=200, tags=["Test"])
async def dummy_user(user_name: str, session: Session = Depends(db.session)):
    """
    dummy 유저를 생성한 후 token을 return 합니다.
    """

    # add dummy user
    user = User(user_name=user_name)
    add_user_result = add_user(session, user)
    if not add_user_result:
        return JSONResponse({"error": "Can't add user"}, status_code=500)

    # get user
    user_result = get_user(session, user_name)
    if not user_result:
        return JSONResponse({"error": "User not found"}, status_code=500)

    # TODO : 더미 유저 생성 후, token도 같이 return
    # get dummy user' token
    token = encode_token(user_name)

    return token


@app.post("/dummy/check", status_code=200, tags=["Test"])
async def dummy_check(
    channel_id: int = Body(default=0),
    user_id: int = Body(default=0),
    session: Session = Depends(db.session),
):
    """
    dummy로 체크할 수 있는 api 입니다. 채널과 유저 아이디를 받아 체크합니다.
    """

    # dummy check
    check = Check(
        check_channel_id=channel_id,
        check_user_id=user_id,
    )
    add_check(session, check)

    # get check
    today = datetime.now()
    check_result = get_check(session, user_id, channel_id, today)

    return check_result
