# -*- coding: utf-8 -*-
import cocos
from cocos.actions import *
from cocos.director import *
from cocos.scene import *
from game_controller import *
import common


def main():
    # initialize director 这是窗口宽、高、名，接口函数
    director.init( width=common.visibleSize["width"], height=common.visibleSize["height"], caption="Flappy Bird")

    # turn off display FPS
    # director.show_FPS = True
    
    #run
    gameScene = Scene()  # 构造场景，接口函数
    game_start(gameScene)

    if director.scene:
        director.replace(gameScene)
    else:
        director.run(gameScene)

