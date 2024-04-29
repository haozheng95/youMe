# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/chat')
def run(ws):
    print(1111111)
    while not ws.closed:
        # 接收发送过来的消息
        message = ws.receive()

        response_text = f"Server receive message: {message}"

        # 向客户端发送消息
        ws.send(response_text)


@app.route('/chat')
def chat():
    print(222)
    # 假设你有一个函数来获取用户信息
    user = {"id":1}
    partner = {"id":2}
    return render_template('chat.html', user=user, partner=partner)


if __name__ == "__main__":
    server = pywsgi.WSGIServer(('localhost', 5678), app, handler_class=WebSocketHandler)
    server.serve_forever()

