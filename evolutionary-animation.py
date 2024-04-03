# import deap
import maya.cmds as cmds
import math


def makeLeg(w, h):
    legPart = cmds.polyCube(width=w, height=h)
    return legPart
    
def makeFloor():
    floor = cmds.polyPlane(width=50, height=50)  
    return floor


def makeBody(bodyW, bodyH, bodyD):
    body = cmds.polyCube( width=bodyW, height=bodyH, depth=bodyD)
    return body
    
def createCreature(legW, legH, bodyW, bodyH, bodyD, spinImp, initVel, rigidS, idx, gravField):
    legs = []
    legPos = []
    pins = []
    
    # create body and move it accordingly
    body = makeBody(bodyW, bodyH, bodyD)
    bodyName = 'body' + str(idx)
    cmds.select(body)
    cmds.rigidBody(act=True, slv=rigidS, m=25, iv=(1,0,0), n=bodyName)
    cmds.move(0, 4, 0, body)
    
    # store positions into an array after calculations
    legPos.append((((bodyW/2)-1.5), 2.5, (1/2+(bodyD/2))))
    legPos.append((((bodyW/2)-1.5), 2.5, -(1/2+(bodyD/2))))
    legPos.append((-((bodyW/2)-1.5), 2.5, (1/2+(bodyD/2))))
    legPos.append((-((bodyW/2)-1.5), 2.5, -(1/2+(bodyD/2))))

    # create all legs
    for i in range(0,4):
        legName = 'calf' + str(i)
        pinName = 'pin' + str(i)
        legs.append(makeLeg(legW, legH))
        cmds.rotate(0, 0, '90deg', legs[i])

        # move legs
        cmds.move(legPos[i][0], legPos[i][1], legPos[i][2], legs[i])

        # make sure each leg is a rigidBody
        cmds.select(legs[i])
        cmds.rigidBody(act=True, b=0, slv=rigidS, imp=legPos[i], si=(0,0,-0.1), m=5, damping=0.4, n=legName)

        pins.append(cmds.constrain(legName, bodyName, hinge=True, n=pinName, p=legPos[i]))

        cmds.connectDynamic(legName, f=gravField)

    creature = cmds.group(body, *legs, *pins, n='creature'+str(idx))

    return creature





cmds.file(new=True, force=True) # make a new scene and don't ask for confirmation

rigidSolver = cmds.rigidSolver(create=True, cu=True, sc=True, si=True, st=True, name='rigidSolver1')

# Set the start and end times
start_time = 0
end_time = 300


# make bounds
floor = makeFloor()
wall = makeFloor()

# set wall
cmds.rotate(0, 0, '90deg', wall)
cmds.move(-25, 25, 0, wall)

# make front legs
calf = makeLeg(4, 2)
calf2 = makeLeg(4, 2)

# make back leg
calf3 = makeLeg(4, 2)
calf4 = makeLeg(4, 2)

# make body
body = makeBody(8, 4, 7)

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
cmds.rigidBody(pas=True, b=0, slv='rigidSolver1', n='floor')  

cmds.select(wall)
cmds.rigidBody(pas=True, b=0, slv='rigidSolver1', n='wall', contactCount=True)

cmds.select(calf)
cmds.rigidBody(act=True, b=0, slv='rigidSolver1', imp=(2.5,4,4), si=(0,0,-0.1), m=5, damping=0.4, n='calf')

cmds.select(calf2)
cmds.rigidBody(act=True, b=0, slv='rigidSolver1', imp=(2.5,4,-4), si=(0,0,-0.1), m=5,  damping=0.4, n='calf10')

cmds.select(calf3)
cmds.rigidBody(act=True, b=0, slv='rigidSolver1', imp=(-2.5,4,4), si=(0,0,-0.1), m=5,  damping=0.4, n='calf11')

cmds.select(calf4)
cmds.rigidBody(act=True, b=0, slv='rigidSolver1', imp=(-2.5,4,-4), si=(0,0,-0.1), m=5,  damping=0.4, n='calf4')

cmds.select(body)
cmds.rigidBody(act=True, slv='rigidSolver1', m=25, iv=(0,0,0), n='body')

# create joints

pin2 = cmds.constrain('calf', 'body', hinge=True, n='pin10', p=(2.5,4,4))

pin4 = cmds.constrain('calf10', 'body', hinge=True, n='pin4', p=(2.5,4,-4))

pin6 = cmds.constrain('calf11', 'body', hinge=True, n='pin6', p=(-2.5,4,4))

pin8 = cmds.constrain('calf4', 'body', hinge=True, n='pin8', p=(-2.5,4,-4))

# have gravity act as a force
gravityField = cmds.gravity(pos=(0, 0, 0), m=9.8, dx=0, dy=-1, dz=0, name='gravityField')
cmds.connectDynamic('calf', f='gravityField')
cmds.connectDynamic('calf10', f='gravityField')
cmds.connectDynamic('calf11', f='gravityField')
cmds.connectDynamic('calf4', f='gravityField')
cmds.connectDynamic('body', f='gravityField')

# create groups
base = cmds.group(calf, calf2, calf3, calf4, body, pin2, pin4, pin6, pin8, n='base')
cmds.move(0,0,0, base)

cmds.setAttr('body.initialVelocityX', 1)
# cmds.setAttr('calf.spinImpulseZ', 10)

# Run the animation
cmds.playbackOptions( minTime='0sec', maxTime='15sec' )

creature = createCreature(4, 2, 8, 4, 7, 0, 0, rigidSolver, 1, gravityField)

# Play the animation
cmds.play()