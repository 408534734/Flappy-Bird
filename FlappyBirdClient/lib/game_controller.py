# -*- coding: utf-8 -*-
import cocos
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *  
from cocos.text  import *
from cocos.menu import *
import random
from atlas import *
from land import *
from bird import *
from score import *
from pipe import *
from collision import *
from network import *
import common
import user
import time

#vars
gameLayer = None#游戏图层，把要显示的东西加进去
gameScene = None#游戏场景对象，要把图层添加进去显示
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
startTime = 0
listener = None
account = None
ipTextField = None
errorLabel = None
isGamseStart = False


def initGameLayer():
	global spriteBird, gameLayer, land_1, land_2
	# gameLayer: 游戏场景所在的layer
	gameLayer = Layer()
	# add background
	bg = createAtlasSprite("bg_day")#加载白天背景，返回元素对象
	bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)#设置白天背景中心位置

	gameLayer.add(bg, z=0)
	'''
	将图层中加入对象
	参数1：要加入的对象
	参数2：放入的图层（从后往前数）
	'''

	# add moving bird
	spriteBird = creatBird()#返回了小鸟对象
	gameLayer.add(spriteBird, z=20)
	# add moving land
	land_1, land_2 = createLand()#两个相连接地面，不断循环向左移动一个屏宽，再回到原点
	gameLayer.add(land_1, z=10, name="land1")
	gameLayer.add(land_2, z=10, name="land2")
	# add gameLayer to gameScene
	gameScene.add(gameLayer)


def game_start(_gameScene):
	global gameScene
	gameScene = _gameScene  # 给全局gameScene赋值
	initGameLayer()  # gameScene添加背景、小鸟、滚动的地
	loginMenu = LoginMenu()
	gameLayer.add(loginMenu, z=20, name="login_menu")


def createLabel(value, x, y):
	label=Label(value,  
		font_name='Times New Roman',  
		font_size=15, 
		color = (0,0,0,255), 
		width = common.visibleSize["width"] - 20,
		multiline = True,
		anchor_x='center',anchor_y='center')
	label.position = (x, y)
	return label


# single game start button的回调函数
def singleGameReady():
	removeContent()
	ready = createAtlasSprite("text_ready")
	ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

	tutorial = createAtlasSprite("tutorial")
	tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
	
	spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])

	#handling touch events
	class ReadyTouchHandler(cocos.layer.Layer):
		is_event_handler = True	 #: enable director.window events

		def __init__(self):
			super( ReadyTouchHandler, self).__init__()

		def on_mouse_press (self, x, y, buttons, modifiers):
			"""This function is called when any mouse button is pressed

			(x, y) are the physical coordinates of the mouse
			'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
			'modifiers' is a bitwise or of pyglet.window.key modifier constants
			   (values like 'SHIFT', 'OPTION', 'ALT')
			"""
			self.singleGameStart(buttons, x, y)
	
		# ready layer的回调函数
		def singleGameStart(self, eventType, x, y):
			isGamseStart = True
			spriteBird.gravity = gravity #gravity is from bird.py
			# handling bird touch events
			addTouchHandler(gameScene, isGamseStart, spriteBird)
			score = 0   #分数，飞过一个管子得到一分
			global startTime
			startTime = time.time()
			# add moving pipes
			pipes = createPipes(gameLayer, gameScene, spriteBird, score)
			# 小鸟AI初始化
			# initAI(gameLayer)
			# add score
			createScoreLayer(gameLayer)
			# add collision detect
			addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2)
			# remove startLayer
			gameScene.remove(readyLayer)

	readyLayer = ReadyTouchHandler()
	readyLayer.add(ready)
	readyLayer.add(tutorial)
	gameScene.add(readyLayer, z=10)

def backToMainMenu():
	restartButton = RestartMenu()
	gameLayer.add(restartButton, z=50, name="restart_button")

def showNotice():
	connected = connect(gameScene) # connect is from network.py
	if not connected:
		content = "Cannot connect to server"
		showContent(content)
	else:
		request_notice() # request_notice is from network.py

def showContent(content):  # 显示提示
	removeContent()
	notice = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
	gameLayer.add(notice, z=70, name="content")

def removeContent():  # 提示消失
	try:
		gameLayer.remove("content")
	except Exception, e:
		pass

def logOut():
	user.user.logout()
	gameScene.remove(gameLayer)
	initGameLayer()
	isGamseStart = False
	# singleGameReady()
	loginMenu = LoginMenu()
	gameLayer.add(loginMenu, z=20, name="login_menu")

import re
usernameItem = None
username = ""
def usernameChange(str):
	try:
		gameLayer.remove("content")
	except:
		pass
	global username, usernameItem
	if len(str) == 9:  # 键入
		if not re.match(r"[a-zA-Z0-9]+", str[8]):
			usernameItem.value = usernameItem.value[:8]
			showContent("Username can only be composed of numbers and letters :(")
		else:
			if len(username) == 8:
				usernameItem.value = usernameItem.value[:8]
				showContent("Username can not longer than 8 :(")
			else:
				p = len(username)
				usernameItem.value = str[0:p] + str[8] + str[p+1:8]
				username = username + str[8]
	else:  # 删除
		if len(username) == 0:
			usernameItem.value = usernameItem.value[:] + u'_'
		else:
			username = username[:len(username)-1]
			p = len(username)
			usernameItem.value = str[0:p] + u'_'*(8-p)
	#print(username)


passwordItem = None
password = ""
def passwordChange(str):
	try:
		gameLayer.remove("content")
	except:
		pass
	global password, passwordItem
	if len(str) == 9:  # 键入
		if not re.match(r"[a-zA-Z0-9]+", str[8]):
			passwordItem.value = passwordItem.value[:8]
			showContent("password can only be composed of numbers and letters :(")
		else:
			if len(password) == 8:
				passwordItem.value = passwordItem.value[:8]
				showContent("password can not longer than 8 :(")
			else:
				p = len(password)
				passwordItem.value = str[0:p] + u"*" + str[p+1:8]
				password = password + str[8]
	else:  # 删除
		if len(password) == 0:
			passwordItem.value = passwordItem.value[:] + u'_'
		else:
			password = password[:len(password)-1]
			p = len(password)
			passwordItem.value = str[0:p] + u'_'*(8-p)

def emptyFunc():
	print("Empty function")
	pass


class LoginMenu(Menu):
	def __init__(self):
		global usernameItem, passwordItem, username, password
		username = ""
		password = ""
		super(LoginMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		usernameItem = (EntryMenuItem("", usernameChange, "________", max_length=9))
		passwordItem = (EntryMenuItem("", passwordChange, "________", max_length=9))
		items = [
			(MenuItem("Username", None)),
			usernameItem,
			(MenuItem("Password", None)),
			passwordItem,
			(ImageMenuItem(common.load_image("button_login.png"), self.login)),
			(ImageMenuItem(common.load_image("button_signup.png"), self.signUp))
		]
		self.font_item_selected['font_size'] = self.font_item['font_size'] = 28
		self.font_item_selected['font_name'] = self.font_item['font_name'] = 'SimHei'
		self.create_menu(items,selected_effect=None,unselected_effect=None)
		connect(gameScene)  # 连接服务器

	def login(self):
		try:
			gameLayer.remove("content")
		except:
			pass
		global username, password
		connect(gameScene)  # 连接服务器
		username = username.encode("ascii")
		password = password.encode("ascii")
		user.userLogin(username, password)

	def signUp(self):
		try:
			gameLayer.remove("content")
		except:
			pass
		global username, password
		connect(gameScene)  # 连接服务器
		username = username.encode("ascii")
		password = password.encode("ascii")
		user.userSignup(username, password)

def loginResult(result):
	if result == "success":
		gameLayer.remove("login_menu")
		start_botton = SingleGameStartMenu()  # 添加菜单
		gameLayer.add(start_botton, z=20, name="start_button")
	else:
		showContent(result)

def signUpResult(result):
	if result == "success":
		gameLayer.remove("login_menu")
		start_botton = SingleGameStartMenu()  # 添加菜单
		gameLayer.add(start_botton, z=20, name="start_button")
	else:
		showContent(result)


class RestartMenu(Menu):
	def __init__(self):  
		super(RestartMenu, self).__init__()
		self.menu_valign = CENTER  
		self.menu_halign = CENTER
		items = [
			(MenuItem(" ", None)),
			(MenuItem(" ", None)),
			(MenuItem(" ", None)),
			(MenuItem(" ", None)),
			(MenuItem(" ", None)),
			(ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
			(ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
			(ImageMenuItem(common.load_image("button_record.png"), showRecord)),
			(ImageMenuItem(common.load_image("button_rank.png"), requestRank)),
			(ImageMenuItem(common.load_image("button_logout.png"), logOut))
		]
		self.create_menu(items)

	def initMainMenu(self):
		gameScene.remove(gameLayer)
		initGameLayer()
		isGamseStart = False
		#singleGameReady()
		difficultyMenu = DifficultyMenu()  # 添加菜单
		gameLayer.add(difficultyMenu, z=20, name="difficulty_button")



class SingleGameStartMenu(Menu):#开始游戏菜单
	def __init__(self):  
		super(SingleGameStartMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [#添加按钮，与点击按钮触发的对象
			(ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
			(ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
			(ImageMenuItem(common.load_image("button_record.png"), showRecord)),
			(ImageMenuItem(common.load_image("button_rank.png"), requestRank)),
			(ImageMenuItem(common.load_image("button_logout.png"), logOut))
		]
		self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

	def gameStart(self):
		gameLayer.remove("start_button")
		#singleGameReady()
		difficultyMenu = DifficultyMenu()  # 添加菜单
		gameLayer.add(difficultyMenu, z=20, name="difficulty_button")


difficulty = 1
aiControl = False


class DifficultyMenu(Menu):
	def __init__(self):
		super(DifficultyMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [  # 添加按钮，与点击按钮触发的对象
			(ImageMenuItem(common.load_image("button_easy.png"), self.setGameEasy)),
			(ImageMenuItem(common.load_image("button_normal.png"), self.setGameNormal)),
			(ImageMenuItem(common.load_image("button_hard.png"), self.setGameHard)),
			(ImageMenuItem(common.load_image("button_Ai.png"), self.setGamAi)),
		]
		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())
		global aiControl
		aiControl= False
	def setGameEasy(self):
		global difficulty
		difficulty = 0.5
		self.gameReady()
	def setGameNormal(self):
		global difficulty
		difficulty = 1
		self.gameReady()
	def setGameHard(self):
		global difficulty
		difficulty = 2
		self.gameReady()
	def setGamAi(self):
		global difficulty
		difficulty = 2
		global aiControl
		aiControl= True
		self.gameReady()
	def gameReady(self):
		gameLayer.remove("difficulty_button")
		land1 = gameLayer.get("land1")
		land2 = gameLayer.get("land2")
		setLandSpeed(land1, land2)
		singleGameReady()

def showRecord():
	try:
		gameLayer.remove("start_button")
		roll_back = "start_button"
	except:
		try:
			gameLayer.remove("restart_button")
			roll_back = "restart_button"
		except:
			pass
	removeContent()
	board = createAtlasSprite("board")
	board.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] / 2)
	gameLayer.add(board, z=60, name="board")

	class Record(Menu):
		def __init__(self, roll_back):
			super(Record, self).__init__("Record")
			self.menu_valign = TOP
			self.menu_halign = CENTER
			self.roll_bacl = roll_back
			items = [
				#(ImageMenuItem(common.load_image("button_record.png"), None)),
				(MenuItem(" ", None)),
				(MenuItem("Rank : " + str(user.user.file[user.user.username]['rank']), None)),
				(MenuItem(" ", None)),
				(MenuItem("Score Time     Data    ", None))
			]
			count = 0
			for i in user.user.file[user.user.username]['record']:
				items.append((MenuItem((str(i[0])+"\t").expandtabs(6)+(str(i[1])+"\t").expandtabs(6)+(i[2]+"\t").expandtabs(11), None)))
				count += 1
				if count == 20:
					break
			items.append(MenuItem(" ", self.close))
			items.append(MenuItem("[ back ]", self.close))
			self.font_item_selected['font_size'] = self.font_item['font_size'] = 13
			self.font_title['font_size'] = 20
			self.font_title['color'] = self.font_item['color'] = self.font_item_selected['color']  # = (0, 0, 0, 255)
			self.font_title['font_name'] = self.font_item_selected['font_name'] = self.font_item['font_name'] = 'SimHei'
			self.create_menu(items)

		def close(self):
			gameLayer.remove("record")
			gameLayer.remove("board")
			if roll_back == "start_button":
				start_botton = SingleGameStartMenu()  # 添加菜单
				gameLayer.add(start_botton, z=20, name="start_button")
			elif roll_back == "restart_button":
				restartButton = RestartMenu()
				gameLayer.add(restartButton, z=50, name="restart_button")
			else:
				showContent("Roll back Error! :(")

	record = Record(roll_back)  # 添加菜单
	gameLayer.add(record, z=61, name="record")

def requestRank():
	showContent("Requesting rank......")
	user.requestRank()

def showRank(rank):
	try:
		gameLayer.remove("start_button")
		roll_back = "start_button"
	except:
		try:
			gameLayer.remove("restart_button")
			roll_back = "restart_button"
		except:
			pass
	removeContent()
	board = createAtlasSprite("board")
	board.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] / 2)
	gameLayer.add(board, z=60, name="board")

	class Rank(Menu):
		def __init__(self, roll_back):
			super(Rank, self).__init__("Rank")
			self.menu_valign = TOP
			self.menu_halign = CENTER
			self.roll_bacl = roll_back
			items = [
				#(ImageMenuItem(common.load_image("button_record.png"), None)),
				(MenuItem(" ", None)),
				(MenuItem("Username Score", None))
			]
			for i in rank:
				items.append(MenuItem((i['username']+"\t").expandtabs(9)+(str(i['bestScore'])+"\t").expandtabs(5), None))
			items.append(MenuItem("[ back ]", self.close))
			self.font_item_selected['font_size'] = self.font_item['font_size'] = 13
			self.font_title['font_size'] = 20
			self.font_title['color'] = self.font_item['color'] = self.font_item_selected['color']  # = (0, 0, 0, 255)
			self.font_title['font_name'] = self.font_item_selected['font_name'] = self.font_item['font_name'] = 'SimHei'
			self.create_menu(items)

		def close(self):
			gameLayer.remove("rank")
			gameLayer.remove("board")
			if roll_back == "start_button":
				start_botton = SingleGameStartMenu()  # 添加菜单
				gameLayer.add(start_botton, z=20, name="start_button")
			elif roll_back == "restart_button":
				restartButton = RestartMenu()
				gameLayer.add(restartButton, z=50, name="restart_button")
			else:
				showContent("Roll back Error! :(")

	rank = Rank(roll_back)  # 添加菜单
	gameLayer.add(rank, z=61, name="rank")