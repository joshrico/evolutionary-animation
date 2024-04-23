# import deap
import maya.cmds as cmds
import math
import random
import sqlite3
import os

db_path = os.path.join('D:\Code Projects\evolutionary-animation', 'creatures.db')


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

    # Check how many entries exist for this generation
    c.execute('SELECT COUNT(*) FROM polyshapes WHERE generation = ?', (generation,))
    count = c.fetchone()[0]

    if count < 3:
        # Insert new creature if fewer than 3 exist
        c.execute('''
            INSERT INTO polyshapes (model_name, generation, body_depth, body_width, body_height, leg_width, leg_height, leg_depth, distance_traveled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (model_name, generation, body_depth, body_width, body_height, leg_width, leg_height, leg_depth, distance_traveled))
        conn.commit()
        print(f"Creature added to generation {generation}.")
    else:
        print(f"Generation {generation} already has 3 creatures.")
        add_polyshape(db_path, model_name, generation+1, body_depth, body_width, body_height, leg_width, leg_height, leg_depth, distance_traveled)

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

def get_highest_generation(db_path):
    """
    Retrieves the highest generation number from the database.

    :param db_path: The file path to the SQLite database.
    :return: The highest generation number or 0 if no data is found.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute('SELECT MAX(generation) FROM polyshapes;')
        max_generation = c.fetchone()[0]

        # If there are no entries, max_generation will be None
        if max_generation is None:
            max_generation = 0

        return max_generation
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()

def makePart(w, h, d, name):
    part = cmds.polyCube(width=w, height=h, depth=d)
    cmds.rename(part[0], name)
    return part[0]

def makeFloor():
    floor = cmds.polyPlane(width=500, height=500)
    return floor

def createCreature(bodyW, bodyH, bodyD, legW, legH, legD, spinImp, initVel, idx, idx2, rigidS, gravField):
    legs = []
    legPos = []
    pins = []

    # create body and move it accordingly
    bodyName = 'body' + str(idx)
    makePart(bodyW, bodyH, bodyD, bodyName)
    cmds.select('body'+str(idx))
    cmds.rigidBody(act=True, slv=rigidS, m=5, iv=initVel, n='rigid'+bodyName)
    cmds.move(0, 4, 0, bodyName)

    # store positions into an array after calculations
    legPos.append((((bodyW/2)-1.5), (bodyH/6), (legD/2+(bodyD/2))))
    legPos.append((((bodyW/2)-1.5), (bodyH/6), -(legD/2+(bodyD/2))))
    legPos.append((-((bodyW/2)-1.5), (bodyH/6), (legD/2+(bodyD/2))))
    legPos.append((-((bodyW/2)-1.5), (bodyH/6), -(legD/2+(bodyD/2))))

    # create all legs
    for i in range(0,4):
        legName = 'calf' + str(idx2+i)
        pinName = 'pin' + str(idx2+i)
        makePart(legW, legH, legD, legName)
        legs.append(legName)
        cmds.rotate(0, 0, '90deg', legName)

        # move legs
        cmds.move(legPos[i][0], legPos[i][1], legPos[i][2], legName)

        # make sure each leg is a rigidBody
        cmds.select(legName)
        cmds.rigidBody(act=True, b=0, slv=rigidS, imp=legPos[i], si=spinImp, m=5, damping=0.4, df=1, n='rigid'+legName)

        pins.append(cmds.constrain(legName, bodyName, hinge=True, n=pinName, p=legPos[i]))

        cmds.connectDynamic(legName, f=gravField)

    creature = cmds.group(bodyName, *legs, *pins, n='creature'+str(idx))

    return creature

def play_animation():
    print('Starting animation...')
    gen = query_by_generation(db_path, get_highest_generation(db_path))
    print(gen)
    # Check if we have enough items to avoid index errors
    if len(gen) < 3:
        print("Not enough items in generation to perform animation.")
        return

    try:
        # # Get initial positions
        # shift1 = cmds.getAttr('body' + str(gen[0][0]) + '.translateX')
        # shift2 = cmds.getAttr('body' + str(gen[1][0]) + '.translateX')
        # shift3 = cmds.getAttr('body' + str(gen[2][0]) + '.translateX')

        shift1 = cmds.getAttr('body1.translateX')
        shift2 = cmds.getAttr('body2.translateX')
        shift3 = cmds.getAttr('body3.translateX')


        print("Initial positions:")
        print(shift1, shift2, shift3)

        # Set playback options
        cmds.playbackOptions(minTime='0sec', maxTime='10sec', animationStartTime='0sec', animationEndTime='10sec', loop='once')

        # Reset current time to the start
        cmds.currentTime('0sec', edit=True)

        # Play the animation
        cmds.play(wait=True)

        # After playback, get new positions
        # shift1 = cmds.getAttr('body' + str(gen[0][0]) + '.translateX')
        # shift2 = cmds.getAttr('body' + str(gen[1][0]) + '.translateX')
        # shift3 = cmds.getAttr('body' + str(gen[2][0]) + '.translateX')

        shift1 = cmds.getAttr('body1.translateX')
        shift2 = cmds.getAttr('body2.translateX')
        shift3 = cmds.getAttr('body3.translateX')

        print("Positions after animation:")
        print(shift1, shift2, shift3)

        # insert distance traveled to database
        update_distance_traveled(db_path, gen[0][0], shift1)
        update_distance_traveled(db_path, gen[1][0], shift2)
        update_distance_traveled(db_path, gen[2][0], shift3)

        # check the database
        gen = query_by_generation(db_path, get_highest_generation(db_path))
        print(gen)

    except Exception as e:
        print(f"Error during animation: {e}")

def reset():
    gen = query_by_generation(db_path, 1)
    for creature in gen:
        if cmds.objExists(creature[1]):
            cmds.delete(creature[1])
        else:
            print(f"Group '{creature}' does not exist.")

def create_generation(rigid_solver, gravity_field):
    print('call create_generation()')
    initial_generation = []

    for i in range(3):  # Simplified loop header
        random_nums = []
        for j in range(12):
            if j < 2:
                random_nums.append(random.uniform(8, 20))
            elif j == 3:
                random_nums.append(random.uniform(1, 5))
            elif j < 5:
                random_nums.append(random.uniform(random_nums[1] / 2, random_nums[1]))
            elif j == 5:
                random_nums.append(random.uniform(random_nums[1] / 2, 4))
            else:
                random_nums.append(random.uniform(1, 5))

        initial_generation.append(random_nums)
        print(initial_generation[i])

        creature_id = createCreature(
            initial_generation[i][0],
            initial_generation[i][1],
            initial_generation[i][2],
            initial_generation[i][3],
            initial_generation[i][4],
            initial_generation[i][5],
            (0, 0, -(initial_generation[i][8])),
            (0, 0, 0),
            i + 1,
            i * 4,
            rigid_solver,  # Assuming these are placeholders
            gravity_field
        )

        # Add the creature to the database with distance traveled as 0
        add_polyshape(db_path, creature_id, 1,  # Assuming generation 1
                      initial_generation[i][0], initial_generation[i][1], initial_generation[i][2],
                      initial_generation[i][3], initial_generation[i][4], initial_generation[i][5], 0)

        # Move logic in Maya (assumes use of cmds, which needs to be defined/imported if using outside of Maya)
        if i == 0:
            cmds.move(0, initial_generation[i][4] * 2, -50, creature_id)
        elif i == 1:
            cmds.move(0, initial_generation[i][4] * 2, 0, creature_id)
        else:
            cmds.move(0, initial_generation[i][4] * 2, 50, creature_id)

def create_generic_gui(rigid_solver, gravity_field):
    window_name = "EvolutionaryAnimation"  # Avoid spaces in the window name to prevent issues
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name, window=True)  # Ensure it's deleting a window

    # Create the window with a fresh layout
    try:
        cmds.window(window_name, title=window_name, widthHeight=(300, 150))
        cmds.columnLayout(adjustableColumn=True)

        # Buttons for different functions
        cmds.button(label="Create Generation", command=lambda x: create_generation(rigid_solver, gravity_field))
        cmds.button(label="Test Generation", command=lambda x: play_animation())
        cmds.button(label="Reset Scene", command=lambda x: print(reset()))

        cmds.showWindow(window_name)  # Make sure to show the window
    except Exception as e:
        print(f"Error creating GUI: {e}")


def main():
    cmds.file(new=True, force=True) # make a new scene and don't ask for confirmation

    create_database(db_path)
    query_polyshapes(db_path)

    rigid_solver = cmds.rigidSolver(create=True, cu=True, sc=True, si=True, st=True, name='rigidSolver1')

    # make bounds
    floor = makeFloor()
    wall = makeFloor()

    # set wall
    cmds.rotate(0, 0, '90deg', wall)
    cmds.move(-250, 250, 0, wall)


    # set physics on each object
    cmds.select(floor)
    cmds.rigidBody(pas=True, b=0, slv=rigid_solver, n='floor')

    cmds.select(wall)
    cmds.rigidBody(pas=True, b=0, slv=rigid_solver, n='wall', contactCount=True)

    # have gravity act as a force
    gravity_field = cmds.gravity(pos=(0, 0, 0), m=9.8, dx=0, dy=-1, dz=0, name='gravityField')

    if not cmds.window('Evolutionary Animation', exists=True):
        create_generic_gui(rigid_solver, gravity_field)
    else:
        print("Window already exists")

    print(query_polyshapes(db_path))

if __name__ == "__main__":
    main()
