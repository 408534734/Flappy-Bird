# -*- coding: UTF-8 -*-
import os
import pyglet

visibleSize = {"width":228, "height":512}#定义窗口大小

THISDIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.normpath(os.path.join(THISDIR, '..', 'data'))

def load_image(path):# 加载图片
    return pyglet.image.load(os.path.join(DATADIR, path))