# import deap
import maya.cmds as cmds
import math
import random
import sqlite3
import os

def create_database(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS polyshapes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            generation INTEGER,
            body_depth REAL,
            body_width REAL,
            body_height REAL,
            leg_width REAL,
            leg_height REAL,
            leg_depth REAL,
            distance_traveled REAL
        );
    ''')
    conn.commit()
    conn.close()

def add_polyshape(db_path, model_name, generation, body_depth, body_width, body_height, leg_width, leg_height, leg_depth, distance_traveled):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO polyshapes (model_name, generation, body_depth, body_width, body_height, leg_width, leg_height, leg_depth, distance_traveled) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
              (model_name, generation, body_depth, body_width, body_height, leg_width, leg_height, leg_depth, distance_traveled))
    conn.commit()
    conn.close()

def query_polyshapes(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM polyshapes')
    polyshapes = c.fetchall()
    conn.close()
    return polyshapes

def update_distance_traveled(db_path, polyshape_id, new_distance):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('UPDATE polyshapes SET distance_traveled = ? WHERE id = ?', (new_distance, polyshape_id))
    conn.commit()
    conn.close()

def query_by_generation(db_path, generation):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM polyshapes WHERE generation = ?', (generation,))
    results = c.fetchall()
    conn.close()
    return results

def makeLeg(w, h, d):
    legPart = cmds.polyCube(width=w, height=h, depth=d)
    return legPart

def makeFloor():
    floor = cmds.polyPlane(width=500, height=500)
    return floor


def makeBody(bodyW, bodyH, bodyD):
    body = cmds.polyCube( width=bodyW, height=bodyH, depth=bodyD)
    return body

def createCreature(bodyW, bodyH, bodyD, legW, legH, legD, spinImp, initVel, idx, idx2, rigidS, gravField):
    legs = []
    legPos = []
    pins = []

    # create body and move it accordingly
    body = makeBody(bodyW, bodyH, bodyD)
    bodyName = 'body' + str(idx)
    cmds.select(body)
    cmds.rigidBody(act=True, slv=rigidS, m=20, iv=initVel, n=bodyName)
    cmds.move(0, 4, 0, body)

    # store positions into an array after calculations
    legPos.append((((bodyW/2)-1.5), (bodyH/6), (legD/2+(bodyD/2))))
    legPos.append((((bodyW/2)-1.5), (bodyH/6), -(legD/2+(bodyD/2))))
    legPos.append((-((bodyW/2)-1.5), (bodyH/6), (legD/2+(bodyD/2))))
    legPos.append((-((bodyW/2)-1.5), (bodyH/6), -(legD/2+(bodyD/2))))

    # create all legs
    for i in range(0,4):
        legName = 'calf' + str(idx2+i)
        pinName = 'pin' + str(idx2+i)
        legs.append(makeLeg(legW, legH, legD))
        cmds.rotate(0, 0, '90deg', legs[i])

        # move legs
        cmds.move(legPos[i][0], legPos[i][1], legPos[i][2], legs[i])

        # make sure each leg is a rigidBody
        cmds.select(legs[i])
        cmds.rigidBody(act=True, b=0, slv=rigidS, imp=legPos[i], si=spinImp, m=5, damping=0.4, n=legName)

        pins.append(cmds.constrain(legName, bodyName, hinge=True, n=pinName, p=legPos[i]))

        cmds.connectDynamic(legName, f=gravField)

    creature = cmds.group(body, *legs, *pins, n='creature'+str(idx))

    return creature

def test_generation():

    shift1 = cmds.getAttr('pCube1.translateX')
    shift2 = cmds.getAttr('pCube6.translateX')
    shift3 = cmds.getAttr('pCube11.translateX')

    print(0)
    print(shift1)
    print(shift2)
    print(shift3)

    # Play the animation
    cmds.playbackOptions( minTime='0sec', maxTime='10sec' )
    cmds.play(w=True)

    shift1 = cmds.getAttr('pCube1.translateX')
    shift2 = cmds.getAttr('pCube6.translateX')
    shift3 = cmds.getAttr('pCube11.translateX')
    print(12)
    print(shift1)
    print(shift2)
    print(shift3)
    

def create_generic_gui():
    window_name = "Evolutionary Animation"
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="Generic Functions Interface", widthHeight=(300, 150))
    cmds.columnLayout(adjustableColumn=True)

    # Buttons for different functions
    cmds.button(label="Create Generation", command=lambda x: print('placeholder for create generation'))
    cmds.button(label="Store Generation", command=lambda x: print('placeholder for store generation'))
    cmds.button(label="Test Generation", command=lambda x: test_generation())

    cmds.showWindow(window_name)


def main():
    cmds.file(new=True, force=True) # make a new scene and don't ask for confirmation

    # Path to the database file
    db_path = os.path.join('D:\Code\evolutionary-animation', 'creatures.db')
    print(db_path)
    create_database(db_path)
    query_polyshapes(db_path)
    creatures = []

    rigidSolver = cmds.rigidSolver(create=True, cu=True, sc=True, si=True, st=True, name='rigidSolver1')

    # Set the start and end times
    start_time = 0
    end_time = 300


    # make bounds
    floor = makeFloor()
    wall = makeFloor()

    # set wall
    cmds.rotate(0, 0, '90deg', wall)
    cmds.move(-250, 250, 0, wall)


    # set physics on each object
    cmds.select(floor)
    cmds.rigidBody(pas=True, b=0, slv='rigidSolver1', n='floor')

    cmds.select(wall)
    cmds.rigidBody(pas=True, b=0, slv='rigidSolver1', n='wall', contactCount=True)

    # have gravity act as a force
    gravityField = cmds.gravity(pos=(0, 0, 0), m=9.8, dx=0, dy=-1, dz=0, name='gravityField')


    # cmds.setAttr('body.initialVelocityX', 1)
    # cmds.setAttr('calf.spinImpulseZ', 10)

    # Run the animation
    cmds.playbackOptions( minTime='0sec', maxTime='15sec' )

    initialGeneration = []

    for i in range(0,3):
        randomNums = []
        for j in range(0, 12):
            if j < 3:
                randomNums.append(random.uniform(8,20))
            elif j >= 3 and j < 5:
                randomNums.append(random.uniform(randomNums[1]/2,randomNums[1]))
            elif j == 5:
                randomNums.append(random.uniform(randomNums[1]/2,4))
            else:
                randomNums.append(random.uniform(1, 5))
        initialGeneration.append(randomNums)
        print(initialGeneration[i])

        creatures.append(createCreature(
            initialGeneration[i][0],
            initialGeneration[i][1],
            initialGeneration[i][2],
            initialGeneration[i][3],
            initialGeneration[i][4],
            initialGeneration[i][5],
            (0, 0, -(initialGeneration[i][8])),
            (0, 0, 0),
            i+1,
            i*4,
            rigidSolver,
            gravityField
        ))

        if i == 0:
            cmds.move(0, initialGeneration[i][4]*2, -50, creatures[i])
        elif i == 1:
            cmds.move(0, initialGeneration[i][4]*2, 0, creatures[i])
        else:
            cmds.move(0, initialGeneration[i][4]*2, 50, creatures[i])




    # creatures.append(createCreature(4, 2, 8, 4, 7, (0,0,-0.1), (1,0,0), 1, 0, rigidSolver, gravityField))
    # creatures.append(createCreature(8, 4, 16, 8, 14, (0,0,2), (4,0,0), 2, 4, rigidSolver, gravityField))
    # cmds.move(40, 5, 0, creatures[1])


    create_generic_gui()

if __name__ == "__main__":
    main()