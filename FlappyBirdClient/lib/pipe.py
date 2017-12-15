# -*- coding: utf-8 -*-
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
import random
from atlas import *
from bird import *
from score import *
import game_controller
import common
import random

# constants
pipeCount = 2
pipeHeight = 320
pipeWidth = 52
pipeDistance = 100  # 上下管道间的距离
pipeInterval = 180  # 两根管道的水平距离
waitDistance = 100  # 开始时第一根管道距离屏幕最右侧的距离
heightOffset = 25   # 管道的高度偏移值
# vars
PIPE_NEW = 0
PIPE_PASS = 1
pipes = {}	#contains nodes of pipes
pipeState = {}	#PIPE_NEW or PIPE_PASS
downPipeYPosition = {}	#朝下pipe的最下侧的y坐标
upPipeYPosition = {}  #朝上pipe的最上侧的y坐标
pipeIndex = 0
gameSceneForAi = None


class ActorModel(object):
	def __init__(self, cx, cy, half_width, half_height,name):
			self.cshape = CircleShape(eu.Vector2(center_x, center_y), radius)
			self.name = name

def createPipes(layer, gameScene, spriteBird, score):
	global g_score, movePipeFunc, calScoreFunc, aiControlFunc, gameSceneForAi
	gameSceneForAi = gameScene
	def initPipe():
		for i in range(0, pipeCount):

			pipeDistance = random.randint(110 - 20 * game_controller.difficulty, 120)
			global heightOffset
			oldOffeset = heightOffset
			heightOffset = random.randint(75 - 60 * game_controller.difficulty, 75 + 60 * game_controller.difficulty)
			pipeInterval = random.randint(200 - 40 * game_controller.difficulty, 210)
			count = 1
			while True:
				if heightOffset >= oldOffeset:
					if pipeInterval - 50 < heightOffset - oldOffeset:
						pipeInterval = random.randint(200 - 40 * game_controller.difficulty, 250)
					else:
						break
				else:
					if (pipeInterval - 160) * 2.5 < oldOffeset - heightOffset:
						pipeInterval = random.randint(200 - 40 * game_controller.difficulty, 250)
					else:
						break
				count += 1
				if count == 10:
					pipeInterval = 300
					break

			#把downPipe和upPipe组合为singlePipe
			downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
			upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
			singlePipe = CocosNode()
			singlePipe.add(downPipe, name="downPipe")
			singlePipe.add(upPipe, name="upPipe")
			
			#设置管道高度和位置
			singlePipe.position=(common.visibleSize["width"] + i*pipeInterval + waitDistance, heightOffset)
			layer.add(singlePipe, z=10)
			pipes[i] = singlePipe
			pipeState[i] = PIPE_NEW
			upPipeYPosition[i] = heightOffset + pipeHeight/2
			downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance

	def movePipe(dt):
		moveDistance = common.visibleSize["width"]/(2*60)*game_controller.difficulty   # 移动速度和land一致
		for i in range(0, pipeCount):
			pipes[i].position = (pipes[i].position[0]-moveDistance, pipes[i].position[1])
			if pipes[i].position[0] < -pipeWidth/2:
				pipeNode = pipes[i]
				pipeState[i] = PIPE_NEW
				next = i - 1
				if next < 0: next = pipeCount - 1

				pipeDistance = random.randint(110-20*game_controller.difficulty, 120)
				global heightOffset
				oldOffeset = heightOffset
				heightOffset = random.randint(75-60*game_controller.difficulty, 75+60*game_controller.difficulty)
				pipeInterval = random.randint(200-40*game_controller.difficulty, 210)
				count = 1
				while True:
					if heightOffset >= oldOffeset :
						if pipeInterval-50 <  heightOffset - oldOffeset:
							pipeInterval = random.randint(200 - 40 * game_controller.difficulty, 250)
						else:
							break
					else:
						if (pipeInterval-160)*2.5 < oldOffeset - heightOffset:
							pipeInterval = random.randint(200 - 40 * game_controller.difficulty, 250)
						else:
							break
					count += 1
					if count == 10:
						pipeInterval = 300
						break

				pipeNode.position = (pipes[next].position[0] + pipeInterval, heightOffset)
				upPipeYPosition[i] = heightOffset + pipeHeight/2
				downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance
				break

	def calScore(dt):
		global g_score
		birdXPosition = spriteBird.position[0]-48
		for i in range(0, pipeCount):
			if pipeState[i] == PIPE_NEW and pipes[i].position[0] < birdXPosition:
				pipeState[i] = PIPE_PASS
				g_score = g_score + 1
				setSpriteScores(g_score) #show score on top of screen

	def aiControl(dt):
		global gameSceneForAi
		if game_controller.aiControl == True:
			nearest = 10000
			for i in range(pipeCount):
				if pipeState[i] == PIPE_NEW and nearest > pipes[i].position[0] - spriteBird.position[0]:
					nearest = pipes[i].position[0] - spriteBird.position[0]
					nearest_i = i
			#print(upPipeYPosition[nearest_i], downPipeYPosition[nearest_i])
			#spriteBird.position = (spriteBird.position[0], upPipeYPosition[nearest_i]+pipeHeight/2)
			if spriteBird.position[1] - 25 <= upPipeYPosition[nearest_i]:
				gameSceneForAi.get("birdTouchHandler").on_mouse_press(None, None, None, None)

	g_score = score
	initPipe()
	movePipeFunc = movePipe
	calScoreFunc = calScore
	aiControlFunc = aiControl
	gameScene.schedule(movePipe)
	gameScene.schedule(calScore)
	gameScene.schedule(aiControl)

	return pipes

def removeMovePipeFunc(gameScene):
	global movePipeFunc
	if movePipeFunc != None:
		gameScene.unschedule(movePipeFunc)

def removeCalScoreFunc(gameScene):
	global calScoreFunc
	if calScoreFunc != None:
		gameScene.unschedule(calScoreFunc)

def removeAiControlFunc(gameScene):
	global aiControlFunc
	if aiControlFunc != None:
		gameScene.unschedule(aiControlFunc)

def getPipes():
	return pipes

def getUpPipeYPosition():
	return upPipeYPosition

def getPipeCount():
	return pipeCount

def getPipeWidth():
	return pipeWidth