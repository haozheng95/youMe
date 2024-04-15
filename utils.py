# 小程序登陆
import json

import requests
import random
import string


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


def send_smscode(code, phone):
    url = "https://apis.shlianlu.com/sms/v2/trade/normal/send"
    appid = "10011712980782749"
    mchid = "1043983"
    signature = "a584c3eb86c3425e8ba9606b4f9f995f"
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }

    data = {"Type": "1",
            "PhoneNumberSet": [phone],
            "AppId": appid,
            "Version": "1.1.0",
            "MchId": mchid,
            "Signature": signature,
            "SessionContext": "您的短信验证码：" + code + "，请在10分钟内输入。",
            "SignName": "【北京焱一文化传媒有限公司】"
            }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json()


def generate_captcha(length):
    """
    生成指定长度的随机验证码
    :param length: 验证码长度
    :return: 随机生成的验证码
    """
    # 定义验证码字符集，包括大写字母、小写字母和数字
    # charset = string.ascii_letters + string.digits
    charset = string.digits

    # 使用random.choices函数从字符集中随机选择指定长度的字符
    captcha = ''.join(random.choices(charset, k=length))
    return captcha


if __name__ == '__main__':
    # 生成一个长度为6的验证码
    captcha = generate_captcha(4)
    # print("生成的验证码是：", captcha)
    send_smscode("123", "15121066738")
    # code = "0c1iGkHa1odsdH0ySTFa1hIosC2iGkHy"
    # print(get_wx_info(code))
