# 小程序登陆
import datetime
import hashlib
import json

import jwt
import requests
import random
import string


def get_wx_info(code):
    appid = 'wx0e24eb45b22f83c3'
    secret = 'e8a245db077272236f94fa5fb993c642'
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code"
    response = requests.get(url)
    return response
    # data = response.json()
    # print(data)
    # openid = data.get('openid')
    # session_key = data.get('session_key')
    # # ... 存储openid和session_key等操作 ...
    # return openid, session_key


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


# 假设你已经在微信开放平台配置了以下信息
APPID = 'wx0e24eb45b22f83c3'
MCHID = '1637086246'
KEY = 'nan3jing3hua3sheng3de3mi3yao1234'
NOTIFY_URL = 'http://yourserver.com/pay/notify'  # 支付结果通知回调地址


# 生成随机字符串
def generate_nonce_str(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# 生成签名
def generate_signature(data):
    sorted_data = sorted(data.items(), key=lambda item: item[0])
    query_string = '&'.join(['{}={}'.format(k, v) for k, v in sorted_data if v is not None])
    query_string += '&key={}'.format(KEY)
    return hashlib.md5(query_string.encode('utf-8')).hexdigest().upper()


# 创建订单
def create_order(openid):
    # 在实际应用中，你应该从数据库中获取或生成订单信息
    return {
        'body': '商品描述',
        'out_trade_no': '123456789',  # 商户订单号
        'total_fee': 1,  # 订单总金额，单位为分
        'openid': openid,  # 小程序用户的openid
        'trade_type': 'JSAPI'  # 交易类型，JSAPI表示小程序支付
    }


# 统一下单接口
def unifiedorder(openid):
    order = create_order(openid)
    order['openid'] = openid

    # 构建统一下单API所需的参数
    params = {
        'appid': APPID,
        'mch_id': MCHID,
        'nonce_str': generate_nonce_str(),
        'body': order['body'],
        'out_trade_no': order['out_trade_no'],
        'total_fee': str(order['total_fee']),
        # 'spbill_create_ip': request.remote_addr,
        'notify_url': NOTIFY_URL,
        'trade_type': order['trade_type'],
        'openid': openid
    }
    params['sign'] = generate_signature(params)

    # 调用微信统一下单API（这里使用requests库，需要先安装）
    response = requests.post(url='https://api.mch.weixin.qq.com/pay/unifiedorder', data=params)
    # result = response.json()  # 假设返回的是JSON格式的数据
    print(response.text)

    # if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
    #     prepay_id = result['prepay_id']
    #     # 生成支付所需的参数并返回给前端
    #     pay_params = {
    #         'appId': APPID,
    #         'timeStamp': str(int(time.time())),
    #         'nonceStr': generate_nonce_str(),
    #         'package': 'prepay_id={}'.format(prepay_id),
    #         'signType': 'MD5'
    #     }
    #     pay_params['paySign'] = generate_signature(pay_params)
    #     return jsonify(pay_params)
    # else:
    #     return jsonify({'error': '支付失败，请重试'}), 500


# 设置你的密钥。在生产环境中，你应该从环境变量或安全的配置管理中获取这个密钥。
SECRET_KEY = 'your-secret-key'

# 设置令牌的过期时间（以秒为单位）
TOKEN_EXPIRATION = 3600 * 24 * 365


# 生成 JWT 令牌
def generate_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=TOKEN_EXPIRATION),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


# 辅助函数：验证 JWT token
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


if __name__ == '__main__':
    # 生成一个长度为6的验证码
    # captcha = generate_captcha(4)
    # print("生成的验证码是：", captcha)
    # send_smscode("123", "15121066738")
    code = "0c1shSkl2Drmjd4i9sml2tBx451shSkg"
    print(get_wx_info(code))
    # openid = "o_rIW4_ZX4_jjfBu86EKQm7Dxx5w"
    # unifiedorder(openid)
