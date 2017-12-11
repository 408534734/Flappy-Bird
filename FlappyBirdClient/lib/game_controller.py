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

#vars
gameLayer = None#游戏图层，把要显示的东西加进去
gameScene = None#游戏场景对象，要把图层添加进去显示
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
account = None
password = None
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
	gameLayer.add(land_1, z=10)
	gameLayer.add(land_2, z=10)
	# add gameLayer to gameScene
	gameScene.add(gameLayer)


def game_start(_gameScene):
	global gameScene
	gameScene = _gameScene  # 给全局gameScene赋值
	initGameLayer()  # gameScene添加背景、小鸟、滚动的地
	start_botton = SingleGameStartMenu()  # 添加菜单
	gameLayer.add(start_botton, z=20, name="start_button")
	connect(gameScene) #连接服务器


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
	gameLayer.add(restartButton, z=50)

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
	

class RestartMenu(Menu):
	def __init__(self):  
		super(RestartMenu, self).__init__()
		self.menu_valign = CENTER  
		self.menu_halign = CENTER
		items = [
				(ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
				(ImageMenuItem(common.load_image("button_notice.png"), showNotice))
				]  
		self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

	def initMainMenu(self):
		gameScene.remove(gameLayer)
		initGameLayer()
		isGamseStart = False
		singleGameReady()

class SingleGameStartMenu(Menu):#开始游戏菜单
	def __init__(self):  
		super(SingleGameStartMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [#添加按钮，与点击按钮触发的对象
				(ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
				(ImageMenuItem(common.load_image("button_notice.png"), showNotice))
				]  
		self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

	def gameStart(self):
		gameLayer.remove("start_button")
		singleGameReady() 


class DifficultyMenu(Menu):
	def __init__(self):
		super(DifficultyMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [  # 添加按钮，与点击按钮触发的对象
			(ImageMenuItem(common.load_image("button_easy.png"), self.gameEasyStart)),
			(ImageMenuItem(common.load_image("button_normal.png"), self.gameNormalStart)),
			(ImageMenuItem(common.load_image("button_hard.png"), self.gameHardStart)),
			(ImageMenuItem(common.load_image("button_Ai.png"), self.gameAiStart)),
		]
		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())