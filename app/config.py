from starlette.config import Config as StarletteConfig
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_ROOT_PASSWORD = 123456
    MYSQL_DATABASE = "uploadChecker"
    MYSQL_USER = "checker"
    MYSQL_PASSWORD = 123456

    MYSQL_PORT = 32072
    MYSQL_HOST = "svc.sel5.cloudtype.app"
    # MYSQL_PORT = 3306
    # MYSQL_HOST = "mysql"
    # KAKAO_REDIRECT_URI = "http://localhost:8000/oauth/kakao/redirect"
    # CLIENT_REDIRECT_URL = "http://localhost:3000/getToken"
    KAKAO_REDIRECT_URI = "https://port-0-upload-checker-server-wr4oe2alqv1116q.sel5.cloudtype.app/oauth/kakao/redirect"
    CLIENT_REDIRECT_URL = (
        "https://web-upload-checker-front-wr4oe2alqv1116q.sel5.cloudtype.app/getToken"
    )

    def __init__(self):
        self.config = StarletteConfig(".env")

    def __call__(self):
        return self.config


config = Config()
