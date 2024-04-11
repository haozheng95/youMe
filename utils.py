# 小程序登陆
import requests


def get_wx_info(code):
    appid = 'wx0e24eb45b22f83c3'
    secret = 'e8a245db077272236f94fa5fb993c642'
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code"
    response = requests.get(url)
    data = response.json()
    print(data)
    openid = data.get('openid')
    session_key = data.get('session_key')
    # ... 存储openid和session_key等操作 ...
    return openid, session_key


if __name__ == '__main__':
    code = "0c1iGkHa1odsdH0ySTFa1hIosC2iGkHy"
    print(get_wx_info(code))
