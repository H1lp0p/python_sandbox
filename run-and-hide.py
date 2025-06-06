import heapq
import random
from playsound import playsound

import colorama


import sys
import os

import base64

colorama.init()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def xor_encrypt(msg: str, key: str) -> str:
    msgb = msg.encode('utf-8')
    keyb = key.encode('utf-8')
    encrypted = bytes([mb ^ keyb[i % len(keyb)] for i, mb in enumerate(msgb)])
    return base64.b64encode(encrypted).decode('utf-8')

def xor_decrypt(encoded_msg: str, key: str) -> str:
    encrypted = base64.b64decode(encoded_msg)
    keyb = key.encode('utf-8')
    decrypted = bytes([b ^ keyb[i % len(keyb)] for i, b in enumerate(encrypted)])
    return decrypted.decode('utf-8')

flag = xor_encrypt(r"HITS{photographer_unknown_presumed_dead}", "slenderman")

w,h = 10, 10
cell_types = {"empty": ".", "tree": "\033[32mT\033[0m", "wall": "#", "player": "\033[36m@\033[0m", "entity": "\033[31m$\033[0m", "exit": "\033[34mE\033[0m"}

pos = (random.randint(0,h - 1), random.randint(0, w // 2))
entity_pos = (random.randint(0, h // 2), random.randint(0, w - 1))
exit_pos = (w - 1, h - 1)

walls_amout = 2 

walls_count = walls_amout

tree_freq = 0.3

notes = [
    "He is coming",
    "Don't look at him",
    "You can't run",
    "He watches us",
    "Help me",
    "You will never leave",
    "He hides in the dark",
    "The end is near"
]

collected = []

win = False

plane = None

def seeding():
    global plane
    new_plane = [["empty" for _ in range(w)] for _ in range(h)]

    for y in range(h):
        for x in range(w):
            if (y,x) == pos: new_plane[y][x] = "player"
            elif (y,x) == entity_pos: new_plane[y][x] = "entity"
            elif (y,x) == exit_pos: new_plane[y][x] = "exit"
            else:
                if random.random() < tree_freq: new_plane[y][x] = random.choice(["tree", "wall"])

    plane = new_plane

    return plane

def ext():
    input("Press enter to exit...")
    quit()

def log(msg):
    print(msg)

def move(dX, dY):
    global pos, collected, win
    if abs(dX) + abs(dY) > 1:
        log(f"Err: move({dX}, {dY}) - To far")
    else:
        nxt_pos = (pos[0] + dY, pos[1] + dX) 
        if nxt_pos[0] < 0 or nxt_pos[0] >= h or nxt_pos[1] < 0 or nxt_pos[1] >=w:
            log(f"Err: move({dX}, {dY}) - you can't run")
        else:
            if plane[nxt_pos[0]][nxt_pos[1]] not in ["entity", "tree", "wall"]: 
                pos = nxt_pos
            elif plane[nxt_pos[0]][nxt_pos[1]] == "tree":
                note = random.choice(notes)
                if note not in collected:
                    collected.append(note)
                    if len(collected) == 8:
                        log("You have grown so much. Do you still afraid of tall people without eyes?")
                        win = True
                        return
                log(f"Note {len(collected)}/{len(notes)}: {note}")
            else:
                log(f"Err: move({dX}, {dY}) - wrong way")
        

def draw():
    for line in plane: print(" ".join([cell_types[cell] for cell in line]))

def entity():
    global entity_pos

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    start = entity_pos
    goal = pos

    # Allowed cells for movement
    walkable = {"empty", "player", "tree"}

    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start))  # (f_score, g_score, position)
    came_from = {}

    g_score = {start: 0}

    while open_set:
        _, current_g, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            if path:
                entity_pos = path[0] 
            return

        neighbors = [
            (current[0] + dy, current[1] + dx)
            for dy, dx in [(0,1),(1,0),(-1,0),(0,-1)]
            if 0 <= current[0] + dy < h and 0 <= current[1] + dx < w
        ]

        for neighbor in neighbors:
            cell_type = plane[neighbor[0]][neighbor[1]]
            if cell_type not in walkable:
                continue

            tentative_g_score = current_g + 1

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, tentative_g_score, neighbor))

def help():
    log(f"{cell_types["player"]} - you, {cell_types["entity"]} - him, {cell_types["exit"]} - exit, {cell_types["tree"]} - tree, {cell_types["wall"]} - wall")
    log("")
    log("move(dX, dY) - move you on [x + dX, y + dY] cell. You can't go more than one cell at the time")
    log(f"wall(dX, dY) - places wall next to you. You have {walls_count} left")
    log(f"cut(dX, dY) - cuts down a tree next to you")
    log("ext() - exit")

def wall(dX, dY):
    global plane, walls_count
    if abs(dX) + abs(dY) > 1:
        log(f"Err: wall({dX}, {dY}) - you can only place wall next to you")
        return
    if (walls_count == 0):
        log(f"Err: wall({dX}, {dY}) - you have no walls left")
        return
    
    pos_to_place = (pos[0] + dY, pos[1] + dX)

    if pos_to_place[0] < 0 or pos_to_place[0] >= h or pos_to_place[1] < 0 or pos_to_place[1] >=w:
        log(f"Err: wall({dX}, {dY}) - for what?")
        return

    if plane[pos_to_place[0]][pos_to_place[1]] == "entity":
        log(f"Err: wall({dX}, {dY}) - too late")
        return
    
    if plane[pos_to_place[0]][pos_to_place[1]] == "exit":
        log(f"Now it's just you and him")
        ext()
        return
    

    plane[pos_to_place[0]][pos_to_place[1]] = "wall"
    walls_count -= 1
    log(f"{walls_count} left")

def cut(dX, dY):
    global plane, walls_count

    if dX == 0 and dY == 0:
        log(f"The only way")
        ext()

    if abs(dX) + abs(dY) > 1:
        log(f"Err: cut({dX}, {dY}) - you can only cut nearby trees")
        return
    
    pos_to_cut = (pos[0] + dY, pos[1] + dX)

    if pos_to_cut[0] < 0 or pos_to_cut[0] >= h or pos_to_cut[1] < 0 or pos_to_cut[1] >=w:
        log(f"Err: cut({dX}, {dY}) - there is nothing here")
        return

    if plane[pos_to_cut[0]][pos_to_cut[1]] == "entity":
        log(f"Err: cut({dX}, {dY}) - not strong enough")
        return
    
    if plane[pos_to_cut[0]][pos_to_cut[1]] == "wall":
        log(f"Err: cut({dX}, {dY}) - this won't work")
        return

    if plane[pos_to_cut[0]][pos_to_cut[1]] == "exit":
        log(f"Now it's just you and him")
        ext()
        return
    
    plane[pos_to_cut[0]][pos_to_cut[1]] = "empty"

def update():
    global plane, win
    new_plane = [[plane[y][x] if plane[y][x] not in ["entity", "player"] else "empty" for x in range(w)] for y in range(h)]

    entity()

    if pos == entity_pos:
        log("It caught you")
        ext()

    win = pos == exit_pos

    new_plane[pos[0]][pos[1]] = "player"
    new_plane[entity_pos[0]][entity_pos[1]] = "entity"

    plane = new_plane

def instruction():
    help()
    log("")
    log("You can't walk through trees, he can. But walls for both of you.")
    log("You don't want to meet him")
    log("Listen. Think. Recollect.")
    log("")
    log("Good luck")

instruction()
while not win:
    if plane == None:
        seeding()
    draw()
    exec(input("> "))
    update()
    if win: 
        log("Do you remember him? Black suit, pale skin, long arms")
        playsound(resource_path("sm_melody.mp3"))
        input("Press enter to exit...")
        log("Try to move into tree") # подло, но зато +реиграбельность

    