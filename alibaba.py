# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys

from typing import List

from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> OpenApiClient:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id="LTAI5tQVPHrHgMqLojBuq5JY",
            access_key_secret="HtDWd6KCZB3nhefpMkZIBFn5YHQ01h"
        )
        config.endpoint = f'dysmsapi.aliyuncs.com'
        return OpenApiClient(config)

    @staticmethod
    def create_api_info() -> open_api_models.Params:
        """
        API 相关
        @param path: params
        @return: OpenApi.Params
        """
        params = open_api_models.Params(
            # 接口名称,
            action='SendSms',
            # 接口版本,
            version='2017-05-25',
            # 接口协议,
            protocol='HTTPS',
            # 接口 HTTP 方法,
            method='POST',
            auth_type='AK',
            style='RPC',
            # 接口 PATH,
            pathname=f'/',
            # 接口请求体内容格式,
            req_body_type='json',
            # 接口响应体内容格式,
            body_type='json'
        )
        return params

    @staticmethod
    def main(telephone, code):
        client = Sample.create_client()
        params = Sample.create_api_info()
        # query params
        queries = {}
        queries['PhoneNumbers'] = telephone
        queries['SignName'] = '南京华盛数新信息科技'
        queries['TemplateCode'] = 'SMS_296721850'
        queries['TemplateParam'] = '{"code":"' + code + '"}'
        # runtime options
        runtime = util_models.RuntimeOptions()
        request = open_api_models.OpenApiRequest(
            query=OpenApiUtilClient.query(queries)
        )
        # 复制代码运行请自行打印 API 的返回值
        # 返回值为 Map 类型，可从 Map 中获得三类数据：响应体 body、响应头 headers、HTTP 返回的状态码 statusCode。
        return client.call_api(params, request, runtime)

    @staticmethod
    async def main_async(
            args: List[str],
    ) -> None:
        client = Sample.create_client()
        params = Sample.create_api_info()
        # query params
        queries = {}
        queries['PhoneNumbers'] = '15121066738'
        queries['SignName'] = '南京华盛数新信息科技'
        queries['TemplateCode'] = 'SMS_296721850'
        queries['TemplateParam'] = '{"code":"111111"}'
        # runtime options
        runtime = util_models.RuntimeOptions()
        request = open_api_models.OpenApiRequest(
            query=OpenApiUtilClient.query(queries)
        )
        # 复制代码运行请自行打印 API 的返回值
        # 返回值为 Map 类型，可从 Map 中获得三类数据：响应体 body、响应头 headers、HTTP 返回的状态码 statusCode。
        await client.call_api_async(params, request, runtime)


if __name__ == '__main__':
    print(Sample.main("15121066738", "1111")["body"]["Message"])
