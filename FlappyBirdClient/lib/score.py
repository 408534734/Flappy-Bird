# -*- coding: utf-8 -*-
from cocos.actions import *
from atlas import *
import common
import user
import time
import game_controller

spriteScores = {}
scoreLayer = None

#开始游戏后显示当前得分
def createScoreLayer(gameLayer):
	global scoreLayer
	scoreLayer = gameLayer
	setSpriteScores(0)

def setSpriteScores(score):
	global scoreLayer
	for k in spriteScores:
		try:
			scoreLayer.remove(spriteScores[k])
			spriteScores[k] = None
		except:
			pass

	scoreStr = str(score)
	i = 0
	for d in scoreStr:
		s = createAtlasSprite("number_score_0"+d)
		s.position = common.visibleSize["width"]/2 + 18 * i, common.visibleSize["height"]*4/5
		scoreLayer.add(s, z=50)
		spriteScores[i] = s
		i = i + 1
	user.user.recordRecentData(score)

def setFinalScore():
	timeCost = cocos.text.Label('Time: ' + getTime(),
								font_name = 'Times New Roman', font_size=18,
								anchor_x='center', anchor_y='center',
								color = (0, 0, 0, 255))
	timeCost.position = common.visibleSize["width"]/2, common.visibleSize["height"]*7/10
	scoreLayer.add(timeCost, 50)
	bestScore = user.user.recordFinalData()
	bestScore = cocos.text.Label('Best: ' + str(bestScore),
								font_name = 'Times New Roman', font_size=18,
								anchor_x='center', anchor_y='center',
								color = (0, 0, 0, 255))
	bestScore.position = common.visibleSize["width"]/2, common.visibleSize["height"]*3/5
	scoreLayer.add(bestScore, 49)
	game_controller.showContent("Uploading your record......")


def getTime():
	second = int(time.time() - game_controller.startTime)
	min = second / 60
	second %= 60
	hour = min / 60
	min %= 60
	back = str(second) + "s"
	if min > 0 or hour > 0:
		back = str(min) + "min " + back
		if hour > 0:
			back = str() + "h " + back
	return back
