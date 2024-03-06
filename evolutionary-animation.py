# import deap
import maya.cmds as cmds
import math


def makeLeg(w, h):
    legPart = cmds.polyCube(width=w, height=h)
    return legPart
    
def makeFloor():
    floor = cmds.polyPlane(width=20, height=20)  
    return floor

def makeBody():
    body = cmds.polyCube( w=8, h=4, d=7 )
    return body

rigidSolver = cmds.rigidSolver(create=True, name='rigidSolver1')

# make front legs
thigh = makeLeg(6, 2)
calf = makeLeg(4, 2)
thigh2 = makeLeg(6, 2)
calf2 = makeLeg(4, 2)

# make back legs
thigh3 = makeLeg(3, 2)
calf3 = makeLeg(4, 2)
thigh4 = makeLeg(3, 2)
calf4 = makeLeg(4, 2)

# make floor
floor = makeFloor()

# make body
body = makeBody()

#move front legs
cmds.move(8, 4, 4, calf)
cmds.move(4, 4, 4, thigh)
cmds.move(8, 4, -4, calf2)
cmds.move(4, 4, -4, thigh2)

#move back legs
cmds.move(0, 4, 4, calf3)
cmds.move(-2, 4, 4, thigh3)
cmds.move(0, 4, -4, calf4)
cmds.move(-2, 4, -4, thigh4)

# set body
cmds.move(0, 4, 0, body)

# set physics on each object
cmds.select(floor)
cmds.rigidBody(passive=True, b=1, solver='rigidSolver1', name='floor')  

cmds.select(thigh)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', name='thigh')

cmds.select(calf)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', damping=0.4, name='calf')

cmds.select(thigh2)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', name='thigh2')

cmds.select(calf2)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', damping=0.4, name='calf2')

cmds.select(thigh3)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', name='thigh3')

cmds.select(calf3)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', damping=0.4, name='calf3')

cmds.select(thigh4)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', name='thigh4')

cmds.select(calf4)
cmds.rigidBody(active=True, b=1, solver='rigidSolver1', damping=0.4, name='calf4')

cmds.select(body)
cmds.rigidBody(active=True, solver='rigidSolver1', name='body')

# create joints

pin = cmds.constrain('thigh', 'calf', pin=True, n='pin', p=(6,4,4))

pin2 = cmds.constrain('thigh', 'body', pin=True, n='pin2', p=(2,4,4))

pin3 = cmds.constrain('thigh2', 'calf2', pin=True, n='pin3', p=(6,4,-4))

pin4 = cmds.constrain('thigh2', 'body', pin=True, n='pin4', p=(2,4,-4))

pin5 = cmds.constrain('thigh3', 'calf3', pin=True, n='pin5', p=(-0.5,4,4))

pin6 = cmds.constrain('thigh3', 'body', pin=True, n='pin6', p=(-3,4,4))

pin7 = cmds.constrain('thigh4', 'calf4', pin=True, n='pin7', p=(-0.5,4,-4))

pin8 = cmds.constrain('thigh4', 'body', pin=True, n='pin8', p=(-3,4,-4))

# have gravity act as a force
cmds.gravity(pos=(0, 0, 0), m=9.8, dx=0, dy=-1, dz=0, name='gravityField')
cmds.connectDynamic('thigh', f='gravityField')
cmds.connectDynamic('calf', f='gravityField')
cmds.connectDynamic('thigh2', f='gravityField')
cmds.connectDynamic('calf2', f='gravityField')
cmds.connectDynamic('thigh3', f='gravityField')
cmds.connectDynamic('calf3', f='gravityField')
cmds.connectDynamic('thigh4', f='gravityField')
cmds.connectDynamic('calf4', f='gravityField')
cmds.connectDynamic('body', f='gravityField')

# create groups
leg = cmds.group(thigh, calf, pin, n='leg')
leg2 = cmds.group(thigh2, calf2, pin3, n='leg2')
leg3 = cmds.group(thigh3, calf3, pin5, n='leg3')
leg4 = cmds.group(thigh4, calf4, pin7, n='leg4')
base = cmds.group(leg, leg2, leg3, leg4, body, pin2, pin4, pin6, pin8, n='base')

# cmds.move(0,4,0, base)


cmds.play(w=True)
