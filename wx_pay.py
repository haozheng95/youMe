import json
import time

import requests
from Crypto.PublicKey import RSA
import random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64


class Authorization(object):
    def __init__(self):
        self.mchid = '1637086246'
        self.serial_no = '30B8E581097C61F3AF3A9DC4943E55DE55249ADC'

    # 生成欲签名字符串
    def sign_str(self, method, url_path, timestamp, nonce_str, request_body):
        if request_body:
            # POST
            sign_list = [
                method,
                url_path,
                timestamp,
                nonce_str,
                request_body
            ]
            return '\n'.join(sign_list) + '\n'
        else:
            # GET
            sign_list = [
                method,
                url_path,
                timestamp,
                nonce_str
            ]
            return '\n'.join(sign_list) + '\n\n'

    # 生成随机字符串
    def getNonceStr(self):
        data = "123456789zxcvbnmasdfghjklqwertyuiopZXCVBNMASDFGHJKLQWERTYUIOP"
        nonce_str = ''.join(random.sample(data, 30))
        return nonce_str

    # 生成签名
    def sign(self, sign_str):
        with open('./apiclient_key.pem', 'r') as f:
            # 这里要注意的秘钥只能有三行
            # -----BEGIN PRIVATE KEY-----
            # ******************秘钥只能在一行，不能换行*****************
            # -----END PRIVATE KEY-----
            private_key = f.read()
            f.close()
            pkey = RSA.importKey(private_key)
            h = SHA256.new(sign_str.encode('utf-8'))
            signature = PKCS1_v1_5.new(pkey).sign(h)
            sign = base64.b64encode(signature).decode()
            return sign

    # 生成 Authorization
    def authorization(self, method, url_path, nonce_str, timestamp, body=None):
        # 加密子串
        signstr = self.sign_str(method=method, url_path=url_path, timestamp=timestamp, nonce_str=nonce_str,
                                request_body=body)
        print("加密原子串：" + signstr)
        # 加密后子串
        s = self.sign(signstr)
        print("加密后子串：" + s)
        authorization = 'WECHATPAY2-SHA256-RSA2048 ' \
                        'mchid="{mchid}",' \
                        'nonce_str="{nonce_str}",' \
                        'signature="{sign}",' \
                        'timestamp="{timestamp}",' \
                        'serial_no="{serial_no}"'. \
            format(mchid=self.mchid,
                   nonce_str=nonce_str,
                   sign=s,
                   timestamp=timestamp,
                   serial_no=self.serial_no
                   )
        return authorization


def wx_pay(body):
    method = "POST"
    url_path = "/v3/pay/transactions/jsapi"
    url = "https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi"
    timestamp = str(int(time.time()))
    nonce_str = Authorization().getNonceStr()
    authorization = Authorization().authorization(method=method, url_path=url_path, nonce_str=nonce_str,
                                                  timestamp=timestamp, body=json.dumps(body))

    header = {
        'Content-Type': 'application/json',
        'Authorization': authorization
    }

    response = requests.post(url, headers=header, json=body)
    return response


def create_wx_pay_body(description, openid, amount):
    appid = 'wx0e24eb45b22f83c3'
    mchid = '1637086246'
    notify_url = 'https://api.mch.weixin.qq.com/v3/notify/jsapi'

    return {'appid': appid, 'mchid': mchid, 'description': description,
            'out_trade_no': Authorization().getNonceStr(), 'notify_url': notify_url,
            'amount': {'total': amount, 'currency': 'CNY'},
            'payer': {'openid': openid}}


if __name__ == '__main__':
    body = create_wx_pay_body('aaaa', 'o_rIW4_ZX4_jjfBu86EKQm7Dxx5w', 1)
    print(wx_pay(body).text)
    # method = "POST"
    # url_path = "/v3/pay/transactions/jsapi"
    # url_path = "/v3/certificates"
    # timestamp = str(int(time.time()))
    # nonce_str = Authorization().getNonceStr()
    # body = {'appid': 'wx0e24eb45b22f83c3', 'mchid': '1637086246', 'description': '爱奇艺周卡',
    #         'out_trade_no': 'LY1111111111', 'notify_url': 'http://127.0.0.1', 'amount': {'total': 1, 'currency': 'CNY'},
    #         'payer': {'openid': 'o_rIW4_ZX4_jjfBu86EKQm7Dxx5w'}}
    # authorization = Authorization().authorization(method=method, url_path=url_path, nonce_str=nonce_str,
    #                                               timestamp=timestamp, body=json.dumps(body))
    # print(1111)
    # print(authorization)
    # print(222)
    # print(json.dumps(body))
