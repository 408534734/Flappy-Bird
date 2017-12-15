# -*- coding: utf-8 -*-
import socket, netstream
import random
import user
connected = False
sock = None

serialID = 0			#server向客户端发回的序列ID号
isSet = False


def connect(gameScene):  # 连接服务器
	global connected, sock
	if connected:
		return connected
	#connect server
	for i in range(5):
		host = "127.0.0.1"
		port = 9234
		sock = socket.socket()
		try:
			sock.connect((host, port))
		except:
			print("Connect Fail!")
			continue
		connected = True
		break

	#始终接收服务端消息
	def receiveServer(dt):
		global connected, serialID
		if not connected:
			return
		data = netstream.read(sock)
		if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
			return
		
		#客户端SID
		if 'sid' in data:
			serialID = data['sid']
		else:
			user.userDataProcess(data)
		'''
		if 'notice_content' in data:
			import game_controller
			game_controller.showContent(data['notice_content']) #showContent is from game_controller
		'''

	gameScene.schedule(receiveServer)
	return connected

def get_send_data():
	send_data = {}
	send_data['sid'] = serialID
	return send_data

#向server请求公告
def request_notice():
	send_data = get_send_data()
	send_data['type'] = 'notice'
	clientSend(send_data)

# 向服务器发送数据
def clientSend(sendData):
	netstream.send(sock, sendData)