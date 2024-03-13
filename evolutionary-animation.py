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
calf = makeLeg(4, 2)
calf2 = makeLeg(4, 2)

# make back leg
calf3 = makeLeg(4, 2)
calf4 = makeLeg(4, 2)

# make floor
floor = makeFloor()

# make body
body = makeBody()

# set body
cmds.move(0, 4, 0, body)

#move front legs
cmds.rotate(0, 0, '90deg', calf)
cmds.rotate(0, 0, '90deg', calf2)
cmds.rotate(0, 0, '90deg', calf3)
cmds.rotate(0, 0, '90deg', calf4)
cmds.move(2.5, 2.5, 4, calf)
cmds.move(2.5, 2.5, -4, calf2)

#move back legs
cmds.move(-2.5, 2.5, 4, calf3)
cmds.move(-2.5, 2.5, -4, calf4)



# set physics on each object
cmds.select(floor)
cmds.rigidBody(passive=True, b=0, solver='rigidSolver1', name='floor')  

cmds.select(calf)
cmds.rigidBody(active=True, b=0.02, solver='rigidSolver1', damping=0.4, name='calf')

cmds.select(calf2)
cmds.rigidBody(active=True, b=0.02, solver='rigidSolver1', damping=0.4, name='calf2')

cmds.select(calf3)
cmds.rigidBody(active=True, b=0.02, solver='rigidSolver1', damping=0.4, name='calf3')

cmds.select(calf4)
cmds.rigidBody(active=True, b=0.02, solver='rigidSolver1', damping=0.4, name='calf4')

cmds.select(body)
cmds.rigidBody(active=True, solver='rigidSolver1', iv=(1,0,0), name='body')

# create joints

#pin = cmds.constrain('thigh', 'calf', pin=True, n='pin', p=(6,4,4))

pin2 = cmds.constrain('calf', 'body', pin=True, n='pin2', p=(2.5,4,4))

#pin3 = cmds.constrain('thigh2', 'calf2', pin=True, n='pin3', p=(6,4,-4))

pin4 = cmds.constrain('calf2', 'body', pin=True, n='pin4', p=(2.5,4,-4))

#pin5 = cmds.constrain('thigh3', 'calf3', pin=True, n='pin5', p=(-0.5,4,4))

pin6 = cmds.constrain('calf3', 'body', pin=True, n='pin6', p=(-2.5,4,4))

#pin7 = cmds.constrain('thigh4', 'calf4', pin=True, n='pin7', p=(-0.5,4,-4))

pin8 = cmds.constrain('calf4', 'body', pin=True, n='pin8', p=(-2.5,4,-4))

# have gravity act as a force
cmds.gravity(pos=(0, 0, 0), m=9.8, dx=0, dy=-1, dz=0, name='gravityField')
cmds.connectDynamic('calf', f='gravityField')
cmds.connectDynamic('calf2', f='gravityField')
cmds.connectDynamic('calf3', f='gravityField')
cmds.connectDynamic('calf4', f='gravityField')

# create groups
base = cmds.group(calf, calf2, calf3, calf4, body, pin2, pin4, pin6, pin8, n='base')

cmds.move(0,4,0, base)

for frame in range(0, 300):
    cmds.currentTime(frame + 1)

    # Move and rotate the cube
    cmds.move(0, 4 * math.sin(math.radians(frame * 6)), 0, base)
    cmds.setKeyframe(base)
    
cmds.playbackOptions( loop='continuous' )
cmds.play(w=True)
