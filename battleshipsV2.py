import numpy as np
import random
import timeit
import matplotlib.pyplot as plt
import matplotlib.animation as animation

ship_shapes = {"oil rig": [(0,0),(0,1),(0,2),(1,1),(2,1),(3,1),(3,0),(3,2)],
               "aircraft carrier": [(0,0),(0,1),(0,2),(0,3),(1,1),(1,2)],
               "destroyer": [(0,0),(0,1),(0,2),(0,3)],
               "sub": [(0,0),(0,1)],
               "speed boat": [(0,0),(0,1),(1,1)]}

ship_sym = {"oil rig": [0,1],
            "aircraft carrier": [0,1,2,3],
            "destroyer": [0,1],
            "sub": [0,1],
            "speed boat": [0,1,2,3]}

island_shape = [(0,0),(0,1),(1,1),(1,0)]

def rotate(offset, orientation):
    if orientation == 0:
        return offset
    elif orientation == 1:
        return (offset[1], -offset[0])
    elif orientation == 2:
        return (-offset[0], -offset[1])
    elif orientation == 3:
        return (-offset[1], offset[0])

class Ship:
    def __init__(self, shape, pos, orientation):
        self.occupied_squares =[]
        self.sunk_squares = []
        self.sunk = False

        for offset in shape:
            self.occupied_squares.append((pos[0]+rotate(offset,orientation)[0], pos[1]+rotate(offset,orientation)[1]))

    def shoot(self, shot):
        if shot in self.occupied_squares and not shot in self.sunk_squares:
            self.sunk_squares.append(shot)
            if len(self.occupied_squares) == len(self.sunk_squares):
                self.sunk = True
                
                return "hit and sunk"
            else:
                return "hit"
        else:
            return ""

class Board:
    def __init__(self):
        self.taken_squares = np.zeros((12,12))
        self.island_positions = []
        for i in range(0,3):
            pos = (random.randrange(0,11),random.randrange(0,11))
            self.island_positions.append(pos)
            ##print(self.island_positions[-1])
            for square in island_shape:
                self.taken_squares[pos[0]+square[0],pos[1]+square[1]] = 1

        self.islands = self.taken_squares.copy() 


        self.ships = {}
        
        for ship_type in ship_shapes:
            while True:
                pos = (random.randrange(0,11),random.randrange(0,11))
                orientation = random.randrange(0,4)
                ship = Ship(ship_shapes[ship_type], pos, orientation)
                if check_valid(ship,self.taken_squares, [])== True:
                    self.ships[ship_type] = ship
                    for square in ship.occupied_squares:
                        self.taken_squares[square] = 1
                    break



        self.finished  = False
        ##plt.imshow(self.taken_squares, cmap='hot', interpolation='nearest')
        ##plt.show()


    def shoot(self, shot):
        status = ""
        for ship in self.ships.values():
            status += ship.shoot(shot)
        if len(status) == 0:
            status = "miss"
        for ship in self.ships.values():
            if ship.sunk ==False:
                break
        else:
            self.finished = True
        return status

def check_valid(ship, taken_squares, hits):
        for square in ship.occupied_squares:
            if not( square[0] >=0 and square[0] <12 and square[1] >=0 and square[1] <12):
                return False
            elif taken_squares[square] == 1:
                return False
        for square in hits:
            if square not in ship.occupied_squares:
                return False
        return True
            
def search(misses, hits, recent_hits):
    heat = np.zeros((12,12))
    for ship_type in ship_shapes:
        for orientation in ship_sym[ship_type]:
            for pos in np.ndindex((12,12)):
                ship = Ship(ship_shapes[ship_type], pos, orientation)
                if check_valid(ship, misses, recent_hits) == True:
                    for square in ship.occupied_squares:
                        heat[square] += 1

    for square in hits:
            heat[square]= 0
    plt.imshow(heat, cmap='hot', interpolation='nearest')
    plt.show()
    ##gif.append([plt.imshow(heat, cmap='hot', interpolation='nearest')])
    return np.unravel_index(heat.argmax(), heat.shape)

def kill(misses, hits, recent_hits):
    heat = np.zeros((12,12))
    
    for ship_type in ship_shapes:
        for orientation in ship_sym[ship_type]:
            reverse_ship = Ship(ship_shapes[ship_type], recent_hits[0], (orientation+2)%4)
            for pos in reverse_ship.occupied_squares:
                ship = Ship(ship_shapes[ship_type], pos, orientation)
                if check_valid(ship, misses, recent_hits) == True:
                    for square in ship.occupied_squares:
                        heat[square] += 1

    ##gif.append([plt.imshow(heat, cmap='hot', interpolation='nearest')])
    plt.imshow(heat, cmap='hot', interpolation='nearest')
    plt.show()
    for square in hits:
            heat[square]= 0
    if np.amax(heat) ==0:
        mode = search
        recent_hits = []
        return mode(misses, hits, recent_hits)
    return np.unravel_index(heat.argmax(), heat.shape)
                        
    
        
def run_game():
    global mode
    global gif
    gif = []
    
    turn = 0
    c = 0 
    board = Board()
    mode = search
    misses = board.islands
    hits = []
    recent_hits = []

    while board.finished == False:
        shot = mode(misses, hits, recent_hits)
        result = board.shoot(shot)
        if result == "miss":
            misses[shot] = 1
        elif result == "hit":
            hits.append(shot)
            recent_hits.append(shot)
            mode = kill         
            c +=1
        else:
            mode = search
            recent_hits = []
            c +=1
        turn +=1
        ##print(shot, result)

    ##print(c)
    ##fig = plt.figure()
    ##ani = animation.ArtistAnimation(fig, gif, interval=200, blit=True, repeat_delay=1000)

    ##ani.save('dynamic_images.mp4')
    ##plt.show()
    return turn



print(run_game())

##total = 0 
##for i in range(0,10):
##    total += run_game()
##print(total/10)


##print(timeit.timeit(run_game, number = 10)/10)
