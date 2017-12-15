# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback, processData

HOST = "127.0.0.1"
disconnected_list = []#断开连接的客户端列表
onlineUser = {}
sid = 0

if __name__ == "__main__":
	s = socket.socket()

	host = HOST#127.0.0.1
	port = 9234

	s.bind((host, port))#绑定IP与端口
	s.listen(4)#最大连接数

	inputs = []#需要监听的socket列表
	inputs.append(s)
	print 'server start! listening host:', host, ' port:', port

while inputs:
	try:
		rs, ws, es = select.select(inputs, [], [])
		'''
		select方法用来监视文件句柄，如果句柄发生变化，则获取该句柄。
		1、当 参数1 序列中的句柄发生可读时（accetp和read），则获取发生变化的句柄并添加到 返回值1 序列中
		2、当 参数2 序列中含有句柄时，则将该序列中所有的句柄添加到 返回值2 序列中
		3、当 参数3 序列中的句柄发生错误时，则将该发生错误的句柄添加到 返回值3 序列中
		4、当 超时时间 未设置，则select会一直阻塞，直到监听的句柄发生变化
		5、当 超时时间 ＝ 1时，那么如果监听的句柄均无任何变化，则select会阻塞 1 秒，之后返回三个空列表，如果监听的句柄有变化，则直接执行。
		'''
		for r in rs:#对于收到的每个连接
			if r is s:#目测是接收到发起的链接
				print 'sid:', sid
				# accept
				connection, addr = s.accept()#获取到socket与IP
				print 'Got connection from' + str(addr)
				inputs.append(connection)#将socket加入监听列表中中
				sendData = {}
				sendData['sid'] = sid
				netstream.send(connection, sendData)

				# 记录每个连接的属性
				cInfo = {}
				cInfo['connection'] = connection
				cInfo['addr'] = str(addr)
				cInfo['ready'] = False
				onlineUser[sid] = cInfo
				print(str(onlineUser))
				sid += 1

			else:# 接收通讯数据
				recvData = netstream.read(r)
				# print 'Read data from ' + str(r.getpeername()) + '\tdata is: ' + str(recvData)
				# 客户端socket关闭
				if recvData == netstream.CLOSED or recvData == netstream.TIMEOUT:
					if r.getpeername() not in disconnected_list:
						print str(r.getpeername()) + 'disconnected'
						disconnected_list.append(r.getpeername())#拓展断开连接的客户端列表

				else:# 根据收到的request发送response
					#公告
					netstream.send(onlineUser[recvData['sid']]['connection'], processData.processData(recvData))
					break
					'''
					if 'notice' in recvData:
						# 获取通讯中某个属性的值
						number = recvData['sid']
						print 'receive notice request from user id:', number
						# 发送数据
						sendData = {"notice_content": "This is a notice from server. Good luck!"}
						netstream.send(onlineUser[number]['connection'], sendData)
					'''
	except Exception:
		traceback.print_exc()
		print 'Error: socket 链接异常'