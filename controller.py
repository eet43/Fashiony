import requests
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

#인증에 필요한 객체 정보, 키 값들 들어가 있음

class Oauth:
    def __init__(self):
        self.auth_server = "https://kauth.kakao.com%s"
        self.api_server = "https://kapi.kakao.com%s"
        self.default_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

    def auth(self, code):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        ).json()

    def userinfo(self, bearer_token):
        return requests.post(
            url=self.api_server % "/v2/user/me",
            headers={
                **self.default_header,
                **{"Authorization": bearer_token}
            },
            data={}
        ).json()
