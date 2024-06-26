import maya.cmds as cmds
import random
import sqlite3
import os
import math

# SQLite database functions
def create_database(db_path):
    # Check if the database file already exists
    if os.path.exists(db_path):
        # Remove the existing file to start fresh
        os.remove(db_path)
        print(f"Existing database removed: {db_path}")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS polyshapes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            generation INTEGER,
            body_width REAL,
            body_height REAL,
            body_depth REAL,
            leg_width REAL,
            leg_height REAL,
            leg_depth REAL,
            spin_imp REAL,
            distance_traveled REAL,
            parent1_id INTEGER,
            parent2_id INTEGER,
            FOREIGN KEY(parent1_id) REFERENCES polyshapes(id),
            FOREIGN KEY(parent2_id) REFERENCES polyshapes(id)
        );
    ''')
    conn.commit()
    conn.close()

def add_creature(db_path, model_name, body_width, body_height, body_depth, leg_width, leg_height, leg_depth, spin_imp, distance_traveled, parent1_id=None, parent2_id=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Use the helper function to get the highest current generation
    max_generation = get_highest_generation(db_path)

    if max_generation == 0:
        generation = 1  # Start with the first generation if the database is empty
    else:
        # Check how many entries exist for the highest generation
        c.execute('SELECT COUNT(*) FROM polyshapes WHERE generation = ?', (max_generation,))
        count = c.fetchone()[0]

        if count < 3:
            generation = max_generation  # Stay in the current generation if fewer than 3 entries
        else:
            generation = max_generation + 1  # Move to the next generation

    # Ensure no parents for the first generation
    if generation == 1:
        parent1_id, parent2_id = None, None

    c.execute('''
        INSERT INTO polyshapes (model_name, generation, body_width, body_height, body_depth, leg_width, leg_height, leg_depth, spin_imp, distance_traveled, parent1_id, parent2_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (model_name, generation, body_depth, body_width, body_height, leg_width, leg_height, leg_depth, spin_imp, distance_traveled, parent1_id, parent2_id))
    conn.commit()
    print(f"Creature added to generation {generation} with model name {model_name}.")
    conn.close()

# SQLite database queries
def query_creatures(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM polyshapes')
    polyshapes = c.fetchall()
    conn.close()
    return polyshapes

def get_lineage(db_path, creature_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT p1.model_name AS parent1_name, p2.model_name AS parent2_name, c.model_name AS child_name
        FROM polyshapes c
        LEFT JOIN polyshapes p1 ON c.parent1_id = p1.id
        LEFT JOIN polyshapes p2 ON c.parent2_id = p2.id
        WHERE c.id = ?
    ''', (creature_id,))
    lineage = c.fetchone()
    conn.close()
    return lineage

def query_by_generation(db_path, generation):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM polyshapes WHERE generation = ?', (generation,))
    results = c.fetchall()
    conn.close()
    return results

def query_by_distance_traveled(db_path, generation):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT distance_traveled FROM polyshapes WHERE generation = ?', (generation,))
    results = c.fetchall()
    conn.close()
    return results

def get_highest_generation(db_path):
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

# SQLite database update
def update_distance_traveled(db_path, polyshape_id, new_distance):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('UPDATE polyshapes SET distance_traveled = ? WHERE id = ?', (new_distance, polyshape_id))
    conn.commit()
    conn.close()

# polyshape construction
def make_part(w, h, d, name):
    part = cmds.polyCube(width=w, height=h, depth=d)
    cmds.rename(part[0], name)
    return part[0]

def make_floor():
    floor = cmds.polyPlane(width=500, height=500)
    return floor

# procedural animation
def create_creature(body_w, body_h, body_d, leg_w, leg_h, leg_d, spin_imp, idx, idx2, rigid_solver, gravity_field):
    # Validate dimensions to prevent physics anomalies
    if body_w <= 0 or body_h <= 0 or body_d <= 0 or leg_w <= 0 or leg_h <= 0 or leg_d <= 0:
        print("Error: All dimensions must be positive.")
        return None

    # Create body and move it accordingly
    body_name = 'body' + str(idx)
    make_part(body_w, body_h, body_d, body_name)
    cmds.select(body_name)
    cmds.rigidBody(act=True, slv=rigid_solver, m=3, b=0, n='rigid' + body_name)
    cmds.connectDynamic(body_name, f=gravity_field)

    legs = []
    leg_pos = []
    pins = []

    # Calculate leg positions to avoid interpenetration
    offsets = [1.5, -1.5]
    for x_offset in offsets:
        for z_offset in offsets:
            # Calculate the base of each leg position
            leg_pos.append((x_offset * (body_w / 2), 0, z_offset * (body_d / 2)))

    # Create all legs
    for i in range(4):  # Four legs
        leg_name = 'calf' + str(idx2 + i)
        pin_name = 'pin' + str(idx2 + i)
        make_part(leg_w, leg_h, leg_d, leg_name)
        legs.append(leg_name)
        cmds.rotate(0, 0, '90deg', leg_name)
        # Position the leg so that the top of the leg is flush with the bottom of the body
        cmds.move(leg_pos[i][0], leg_h, leg_pos[i][2], leg_name)

        cmds.select(leg_name)
        cmds.rigidBody(act=True, b=0, slv=rigid_solver, imp=leg_pos[i], si=spin_imp, m=1, damping=0.4, df=1, n='rigid' + leg_name)

        # Calculate pin position at the top of the legs
        pin_position = (leg_pos[i][0], leg_h, leg_pos[i][2])
        pins.append(cmds.constrain(leg_name, body_name, hinge=True, n=pin_name, p=pin_position))
        cmds.connectDynamic(leg_name, f=gravity_field)

    # Position the body above the legs
    body_elevation = leg_h + 0.5  # Ensure the body is positioned above the legs by a small clearance
    cmds.move(0, body_elevation, 0, body_name)

    # Group all components into a single creature entity
    creature = cmds.group(body_name, *legs, *pins, n='creature' + str(counter))

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
        # Set playback options
        cmds.playbackOptions(minTime='0sec', maxTime='15sec', animationStartTime='0sec', animationEndTime='15sec', loop='once')

        # Reset current time to the start
        cmds.currentTime('0sec', edit=True)

        # Play the animation
        cmds.play(wait=True)

        # insert distance traveled to database
        update_distance_traveled(db_path, gen[0][0], cmds.getAttr('body1.translateX'))
        update_distance_traveled(db_path, gen[1][0], cmds.getAttr('body2.translateX'))
        update_distance_traveled(db_path, gen[2][0], cmds.getAttr('body3.translateX'))

        # check the database
        gen = query_by_generation(db_path, get_highest_generation(db_path))
        print(gen)

        fit = []
        # print(query_by_distance_traveled(db_path, get_highest_generation(db_path)))
        fit.append(fitness(cmds.getAttr('body1.translateX')))
        fit.append(fitness(cmds.getAttr('body2.translateX')))
        fit.append(fitness(cmds.getAttr('body3.translateX')))

        print(fit)
        print(max(fit))

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
        for j in range(7):
            if j < 3:
                random_nums.append(random.uniform(4, 8))
            elif j < 5:
                random_nums.append(random.uniform(random_nums[1], random_nums[1]*1.25))
            elif j == 5:
                random_nums.append(random.uniform(random_nums[1]/2, random_nums[1]))
            else:
                random_nums.append(random.uniform(-3.0, 3.0))

        initial_generation.append(random_nums)
        print(initial_generation[i])

        creature_id = create_creature(
            initial_generation[i][0],
            initial_generation[i][1],
            initial_generation[i][2],
            initial_generation[i][3],
            initial_generation[i][4],
            initial_generation[i][5],
            (0, 0, -(initial_generation[i][6])),
            i + 1,
            i * 4,
            rigid_solver,  # Assuming these are placeholders
            gravity_field
        )

        # Add the creature to the database with distance traveled as 0
        add_creature(db_path, creature_id, initial_generation[i][0], initial_generation[i][1], initial_generation[i][2],
                      initial_generation[i][3], initial_generation[i][4], initial_generation[i][5], initial_generation[i][6], 0)

        # Move logic in Maya (assumes use of cmds, which needs to be defined/imported if using outside of Maya)
        if i == 0:
            cmds.move(0, initial_generation[i][1], -50, creature_id)
        elif i == 1:
            cmds.move(0, initial_generation[i][1], 0, creature_id)
        else:
            cmds.move(0, initial_generation[i][1], 50, creature_id)
        # counter += 1

# evolutionary functions
def fitness(distance_traveled):
    # Handle non-numeric and None values
    try:
        if distance_traveled is None or distance_traveled == 0:
            return float('-inf')  # Use negative infinity to ensure these rank last
        return -distance_traveled ** 2  # Negative because lower distances are better, invert for sorting
    except TypeError:
        return float('-inf')

def select_parents(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Automatically determine the most recent generation
    current_generation = get_highest_generation(db_path)
    if current_generation == 0:
        print("No generations found in the database.")
        return []

    c.execute('''
        SELECT id, body_width, body_height, body_depth, leg_width, leg_height, leg_depth, spin_imp, distance_traveled
        FROM polyshapes
        WHERE generation = ?
    ''', (current_generation,))
    creatures = c.fetchall()
    conn.close()

    # Print fetched data for debugging
    print('Fetched creatures:', creatures)

    # Apply the fitness function to distance_traveled and sort the results
    creatures = sorted(creatures, key=lambda x: fitness(x[8]))  # Ensure using the correct index for distance_traveled

    # Print sorted creatures for debugging
    print('Sorted creatures:', creatures)

    # Select the top 2 performers based on the best fitness values (lowest if negative is better)
    return creatures[:2]

def cross_breed(parent1, parent2):
    child = {
        'body_width': random.choice([parent1['body_width'], parent2['body_width']]),
        'body_height': random.choice([parent1['body_height'], parent2['body_height']]),
        'body_depth': random.choice([parent1['body_depth'], parent2['body_depth']]),
        'leg_width': random.choice([parent1['leg_width'], parent2['leg_width']]),
        'leg_height': random.choice([parent1['leg_height'], parent2['leg_height']]),
        'leg_depth': random.choice([parent1['leg_depth'], parent2['leg_depth']]),
        'spin_imp': random.choice([parent1['spin_imp'], parent2['spin_imp']]),  # Choose the spin impulse
    }

    return child

def mutate(creature, mutation_rate=0.2):
    # Randomly mutate attributes by a factor determined by mutation_rate
    for key in creature:
        if random.random() < mutation_rate:  # 10% chance of mutation
            mutation_factor = random.uniform(0.9, 1.1)  # 10% decrease or increase
            creature[key] *= mutation_factor

    return creature

def next_generation(rigid_solver, gravity_field):
    # Fetch two parents from the most recent generation
    parents = select_parents(db_path)
    if len(parents) < 2:
        print("Not enough parents to perform crossbreeding.")
        return

    # Convert tuples from SQL to dictionaries, including 'spin_imp'
    parent1 = dict(zip(['id', 'body_width','body_height', 'body_depth', 'leg_width', 'leg_height', 'leg_depth', 'spin_imp', 'distance_traveled'], parents[0]))
    parent2 = dict(zip(['id', 'body_width','body_height', 'body_depth', 'leg_width', 'leg_height', 'leg_depth', 'spin_imp', 'distance_traveled'], parents[1]))

    positions = [-50, 0, 50]  # Positions for each new creature

    for i in range(3):  # Create three new creatures
        # Create a child by crossbreeding
        child = cross_breed(parent1, parent2)

        # Mutate the child to introduce variability
        child = mutate(child)

        # Generate a unique model name for each new creature
        model_name = create_creature(
            child['body_width'],
            child['body_height'],
            child['body_depth'],
            child['leg_width'],
            child['leg_height'],
            child['leg_depth'],
            (0, 0, child['spin_imp']),
            i + 1,
            i * 4,
            rigid_solver,
            gravity_field)

        # Add the new child to the database, including 'spin_imp'
        add_creature(db_path, model_name, child['body_width'], child['body_height'], child['body_depth'], child['leg_width'], child['leg_height'], child['leg_depth'], child['spin_imp'], 0,  parent1_id=parent1['id'], parent2_id=parent2['id'])

        # Position the creature in Maya using its model name and generation-specific coordinates
        body_height = child['body_height']  # Using body_height for vertical positioning
        cmds.move(0, body_height, positions[i], model_name)

        print(f"New creature created and positioned: {model_name}")


def create_generic_gui(rigid_solver, gravity_field):
    window_name = "EvolutionaryAnimation"
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name, window=True)

    generation_display = None  # This will hold the UI element displaying the generation number

    def update_generation_display():
        highest_generation = get_highest_generation(db_path)
        if generation_display is not None:
            cmds.text(generation_display, edit=True, label=f"Current Generation: {highest_generation}")

    def create_or_continue():
        reset()  # Reset the scene before creating or continuing a generation
        # Determine which generation creation function to use dynamically
        highest_generation = get_highest_generation(db_path)
        if highest_generation == 0:
            # If no generation exists, use initial generation creation
            create_generation(rigid_solver, gravity_field)
        else:
            # If generations exist, use next generation creation
            next_generation(rigid_solver, gravity_field)
        update_generation_display()
        play_animation()

    try:
        cmds.window(window_name, title=window_name, widthHeight=(300, 150))
        cmds.columnLayout(adjustableColumn=True)

        # Button to create or continue generation with scene reset
        cmds.button(label="Create/Continue Generation", command=lambda x: create_or_continue())

        # Display current generation number
        generation_display = cmds.text(label="Current Generation: 0")

        # Update the display at GUI startup
        update_generation_display()

        cmds.showWindow(window_name)
    except Exception as e:
        print(f"Error creating GUI: {e}")

# driver code
def main():
    cmds.file(new=True, force=True) # make a new scene and don't ask for confirmation

    global db_path
    global counter

    # check if folder exists for creature database
    if os.path.exists('D:\Code\evolutionary-animation'):
        db_path = os.path.join('D:\Code\evolutionary-animation', 'creatures.db')
    elif os.path.exists('D:\Code Projects\evolutionary-animation'):
        db_path = os.path.join('D:\Code Projects\evolutionary-animation', 'creatures.db')
    counter = 1 
    create_database(db_path)
    query_creatures(db_path)

    rigid_solver = cmds.rigidSolver(create=True, cu=True, sc=True, si=True, st=True, name='rigidSolver1')

    # make bounds
    floor = make_floor()

    # set physics on each object
    cmds.select(floor)
    cmds.rigidBody(pas=True, b=0, slv=rigid_solver, n='floor')

    # have gravity act as a force
    gravity_field = cmds.gravity(pos=(0, 0, 0), m=9.8, dx=0, dy=-1, dz=0, name='gravityField')

    if not cmds.window('Evolutionary Animation', exists=True):
        create_generic_gui(rigid_solver, gravity_field)
    else:
        print("Window already exists")

    print(query_creatures(db_path))

if __name__ == "__main__":
    main()
