import json
import time
from random import choice, randint

import pygame
from pygame.locals import *

from variables import *

pygame.init()
def text(string,color=(128,128,128),size=32,font='sansbold',smooth=True):
    return pygame.font.SysFont(font, size).render(string,smooth,color)
def walls_get(walls,width=16,offset=0,chonks=0):
    return [
        Rect(x*width+offset,y*width+offset,width+chonks,width+chonks) for x,y in walls
    ]

resources = json.loads(open("pacman_points.json",'r').read())

class Main():
    def __init__(self,maxfps=0,fill=(0,0,0),language=1):
        resources["resolution"] =  [resources["resolution"][0],resources["resolution"][1]+32,]
        self.screen = pygame.display.set_mode(resources["resolution"])
        self.w,self.h = resources["resolution"]
        self.clock = pygame.time.Clock()
        self.maxfps = maxfps
        self.fill = fill
        self.loop = 0
        self.timestart = time.time()
        self.time = 0
        self.points = 0
        self.centerb = (16,8)
        self.run = 1
        self.player = Player()
        self.lang = language
        self.langs = ("czech","english","french")
        self.languages = json.loads(open('languages.json','r').read())
        self.language = self.languages[self.langs[self.lang]]
        self.ghost_startpos = resources["start_ghost"]
        self.ghosts = [Ghost(startpos=i) for i in self.ghost_startpos]
        self.objects = self.ghosts+[self.player]
        self.visible_walls = walls_get(resources["wall"])
        self.walls = self.visible_walls+walls_get(resources["empty"])
        self.fruit_points = walls_get(resources["road"],offset=8)
        self.fruit = [choice(self.fruit_points),self.time,(randint(0,255),randint(0,255),randint(0,255))]
        self.pellets = walls_get(resources["road"],offset=8)
        self.maxpellets = len(self.pellets)
        print(self.fruit[0])

        
        pygame.mixer.music.play(-1)

    def stop(self):
        self.run = 0
    def tick(self):
        self.dt = self.clock.tick(self.maxfps)
        self.loop += 1
        self.time = time.time()-self.timestart
        self.fps = round(self.clock.get_fps())
    def draw(self):
        self.screen.fill(self.fill)

        for wall in self.visible_walls:
            pygame.draw.rect(self.screen, (27,3,163), wall)

        for pellet in self.pellets:
            pygame.draw.circle(self.screen, (255,255,255), pellet.topleft, 3)

        pygame.draw.circle(self.screen, self.player.color, self.player.pos, self.player.width)
        pygame.draw.circle(self.screen, self.fruit[2], self.fruit[0].topleft, 8)

        for ghost in self.ghosts:
            pygame.draw.circle(self.screen, ghost.color, ghost.pos, ghost.width)
        


        self.screen.blit(text(self.language["fps"]   +str(self.fps),              size=24),(0,self.h-32))
        self.screen.blit(text(self.language["time"]  +str(int(self.time)),        size=24),(0,self.h-16))
        self.screen.blit(text(self.language["points"]+str(int(self.points)),      size=24),(128,self.h-32))
        self.screen.blit(text(self.language["lives"] +str(int(self.player.lives)),size=24),(128,self.h-16))
        self.screen.blit(text(self.language["language"]                          ,size=18),(self.w-200,self.h-32))
        self.screen.blit(text(self.language["language2"]                         ,size=18),(self.w-200,self.h-16))

        pygame.display.flip()
    def logic(self):

        self.player.hitbox = Rect(self.player.pos,(16,16))

        if self.player.pos[0] < 0:
            self.player.pos[0] = self.w
        if self.player.pos[0] > self.w:
            self.player.pos[0] = 0
        if self.player.pos[1] < 0 :
            self.player.pos[1] = self.h
        if self.player.pos[1] > self.h:
            self.player.pos[1] = 0
            
        div0 = self.player.pos[0]%self.centerb[0]
        div1 = self.player.pos[1]%self.centerb[0]
        
        if self.player.moving[0] not in (LEFT,RIGHT):
            if   div0 != self.centerb[1]:
                print("correction x to:",self.player.pos)
                self.player.pos[0] += self.centerb[1]-div0
        if self.player.moving[0] not in (UP,DOWN):
            if   div1 != self.centerb[1]:
                print("correction y to:",self.player.pos)
                self.player.pos[1] += self.centerb[1]-div1

        for i in range(len(self.ghosts)):
            if (
               self.ghosts[i].pos[0] <= 0
            or self.ghosts[i].pos[0] >= self.w
            or self.ghosts[i].pos[1] <= 0
            or self.ghosts[i].pos[1] >= self.h
            ):
                self.ghosts[i].pos = choice(self.ghost_startpos)
                self.ghosts[i].speed = 1
            
            div0 = self.ghosts[i].pos[0]%self.centerb[0]
            div1 = self.ghosts[i].pos[1]%self.centerb[0]

            if self.ghosts[i].moving[0] not in (LEFT,RIGHT):
                if   div0 != self.centerb[1]:
                    self.ghosts[i].pos[0] += self.centerb[1]-div0
            if self.ghosts[i].moving[0] not in (UP,DOWN):
                if   div1 != self.centerb[1]:
                    self.ghosts[i].pos[1] += self.centerb[1]-div1

            if self.player.hitbox.collidepoint(self.ghosts[i].pos) and time.time()-self.player.invincible > 2:
                self.player.invincible = time.time()
                self.player.lives -= 1
                hit.play()

            copy = self.ghosts[:]
            copy.remove(self.ghosts[i])
            if self.ghosts[i].pos in [i.pos for i in copy]:
                self.ghosts[i].pos = choice(self.ghost_startpos)
        self.player.color = (
            (
                (
                    (255,255,255) if self.player.color == (255,0,0) 
                    else (255,0,0)
                ) 
                if self.loop%10==0 else self.player.color
            )
                if  time.time()-self.player.invincible < 2 else (255,255,255)
        )


        if self.player.lives <= 0:
            die.play()
            time.sleep(4)
            self.stop()

        if self.fruit[0].collidepoint(self.player.pos):
            eat.play()
            self.points += 20
            self.fruit = [choice(self.fruit_points),self.time,(randint(0,255),randint(0,255),randint(0,255))]
            if self.points%20 in tuple(range(20)):
                for i in range(len(self.ghosts)):
                    self.ghosts[i].speed += self.ghosts[i].speed/100
            if self.points%50 in tuple(range(20)):
                self.ghosts += [Ghost(startpos=choice(self.ghost_startpos))]
            if self.points%200 in tuple(range(20)):
                self.player.lives += 1

        if self.time-self.fruit[1] > 10:
            self.fruit = [choice(self.fruit_points),self.time,(randint(0,255),randint(0,255),randint(0,255))]
            lost.play()


        for i in range(len(self.pellets)):
            try:
                if self.pellets[i].collidepoint(self.player.pos):
                    self.points += 1
                    self.pellets.pop(i)
                    if self.points%20 == 0:
                        for i in range(len(self.ghosts)):
                            self.ghosts[i].speed += self.ghosts[i].speed/100
                    if self.points%50 == 0:
                        self.ghosts += [Ghost(startpos=choice(self.ghost_startpos))]
                    if self.points%200 == 0:
                        self.player.lives += 1
            except:
                pass
        if len(self.pellets) < self.maxpellets/2:
            self.pellets += [choice(self.fruit_points)]



    def events(self):
        pressed = pygame.key.get_pressed()
        key = 0
        for event in pygame.event.get():
            if event.type == QUIT:
                self.stop()
            elif event.type == KEYDOWN:
                key = event.key
                if key == K_F4 and pressed[K_LALT]:
                    self.stop()
                if key == K_TAB:
                    self.lang = self.lang+1 if self.lang+1 < len(self.langs) else 0
                    self.language = self.languages[self.langs[self.lang]]
                

                if pressed[K_1]:
                    for i in range(len(self.ghosts)):
                        self.ghosts[i].speed += self.ghosts[i].speed/5
                elif pressed[K_2]:
                    for i in range(len(self.ghosts)):
                        self.ghosts[i].speed -= self.ghosts[i].speed/5

                if pressed[K_3]:
                    self.ghosts += [Ghost(startpos=choice(self.ghost_startpos))]
                elif pressed[K_4]:
                    self.ghosts.pop(randint(0,len(self.ghosts)-1))

        try:
            if pressed[K_SPACE]:
                print("zoooooom")
                self.player.speed_fake = 1
                self.player.speed *= 3/2
            if self.player.speed_fake:
                self.player.speed_fake = 0
                self.player.speed *= 2/3
        except:
            pass
            

        print(self.player.pos,[i%16 for i in self.player.pos],self.player.moving," | ",[i.pos for i in self.ghosts])
        # '|',[([i.moving],i.pos) for i in self.ghosts])

        for i in range(len(self.ghosts)):
            self.ghosts[i].random()
            
            self.ghosts[i].colliders = [
                [   
                    (
                        int(self.ghosts[i].pos[0]+k[j][0]*self.ghosts[i].collision),
                        int(self.ghosts[i].pos[1]+k[j][1]*self.ghosts[i].collision)
                    ) 
                    for j in (0,1)
                ]
                for k in (
                    ((-0.5,-1),( 0.5,-1)),
                    (( 0.5, 1),(-0.5, 1)),
                    ((-1,-0.5),(-1, 0.5)),
                    (( 1, 0.5),( 1,-0.5))
                )
            ]
            self.ghosts[i].history = self.ghosts[i].history if self.ghosts[i].moving[0] == None else self.ghosts[i].moving[0]
            if self.ghosts[i].moving[0] != None: # if moving
                self.ghosts[i].move(self.ghosts[i].moving[0],self.dt) # move the player

                if any([
                    any(
                        [k.collidepoint(j) for j in 
                        self.ghosts[i].colliders[self.ghosts[i].moving[0]]]
                    ) for k in self.walls
                ]): # if you are in front of a wall
                    if self.ghosts[i].moving[1] != None: # if you wwant to go to a side
                        self.ghosts[i].moving = [self.ghosts[i].moving[1],None]
                    else: # if you don't want to go to the side
                        self.ghosts[i].moving = [None,None]

            if self.ghosts[i].moving[1] != None: # if you want to move in a different direction
                if not any([
                    any(
                        [k.collidepoint(j) for j in 
                        self.ghosts[i].colliders[self.ghosts[i].moving[1]]]
                    ) for k in self.walls
                ]): # if there is no wall blocking you
                    self.ghosts[i].moving = [self.ghosts[i].moving[1],None]
            
        # ===========================================================================

        self.colliders = [
            [   
                (
                    int(self.player.pos[0]+i[j][0]*self.player.collision),
                    int(self.player.pos[1]+i[j][1]*self.player.collision)
                ) 
                for j in (0,1)
            ] 
            for i in (
                ((-0.5,-1),( 0.5,-1)),
                (( 0.5, 1),(-0.5, 1)),
                ((-1,-0.5),(-1, 0.5)),
                (( 1, 0.5),( 1,-0.5))
            )
        ]
        self.player.history = self.player.history if self.player.moving[0] == None else self.player.moving[0]
        if self.player.moving[0] != None: # if moving
            self.player.move(self.player.moving[0],self.dt) # move the player

            if any([
                any(
                    [i.collidepoint(j) for j in 
                    self.colliders[self.player.moving[0]]]
                ) for i in self.walls
            ]): # if you are in front of a wall
                if self.player.moving[1] != None: # if you wwant to go to a side
                    self.player.moving = [self.player.moving[1],None]
                else: # if you don't want to go to the side
                    self.player.moving = [None,None]

        if self.player.moving[1] != None: # if you want to move in a different direction
            if not any([
                any(
                    [i.collidepoint(j) for j in 
                    self.colliders[self.player.moving[1]]]
                ) for i in self.walls
            ]): # if there is no wall blocking you
                self.player.moving = [self.player.moving[1],None]
            # elif self.player.moving[0] == None:
            #     self.player.moving = [None,self.player.history]
        
        for x in (
            (UP,K_UP),(DOWN,K_DOWN),(LEFT,K_LEFT),(RIGHT,K_RIGHT)
        ):
            if key == x[1]: # if pressed[x[1]]
                if not any([
                    any(
                        [i.collidepoint(j) for j in 
                        self.colliders[x[0]]]
                    ) for i in self.walls
                ]): # if there is no wall blocking you
                    self.player.moving = [x[0],None]
                else:# if there is a wall blocking you
                    self.player.moving[1] = x[0]

class Ghost():
    def __init__(self,speed=1,maxspeed=4,color=(128,128,128),startpos=(224,376),startface = LEFT,width=8,delay=20,res=(512-64,512+16)):
        self.w,self.h = res
        self.pos = list(startpos)
        self.speed = speed
        self.maxspeed = maxspeed
        self.color = color
        self.width = width
        self.collision = width+1
        self.moving = [startface,None]
        self.alive = True
        self.mode = 'r'
        self.history = startface
        self.dtslow = 7
        self.hitbox = Rect(self.pos,(16,16))
        self.delay = delay
        self.wanted = choice(resources["wanted"])

    def move(self,rot,dt):
        x,y = ((0,-1),(0,1),(-1,0),(1,0))[rot]
        self.pos[0] += (int(x * self.speed * (dt if dt < 20 else 20)/self.dtslow) 
                        if int(x * self.speed * (dt if dt < 20 else 20)/self.dtslow) < self.maxspeed 
                        else self.maxspeed)
        self.pos[1] += (int(y * self.speed * (dt if dt < 20 else 20)/self.dtslow) 
                        if int(y * self.speed * (dt if dt < 20 else 20)/self.dtslow) < self.maxspeed 
                        else self.maxspeed)
        if self.speed > 4:
            self.speed = 4

    def random(self):
        try:
            next_possible1 = [(UP,DOWN),(LEFT,RIGHT),(UP,DOWN),(LEFT,RIGHT),(UP,DOWN),(LEFT,RIGHT)][self.moving[0]]
        except:
            next_possible1 = [None]
        try:
            next_possible2 = [(LEFT,RIGHT),(UP,DOWN),(LEFT,RIGHT),(UP,DOWN),(LEFT,RIGHT),(UP,DOWN)][self.moving[0]+1]
        except:
            next_possible2 = [LEFT,RIGHT,UP,DOWN]
        
        weight = []
        if self.wanted[0] > self.pos[0] and self.pos[0] not in tuple(range(self.wanted[0]-32,self.wanted[0]+32)):
            weight += [RIGHT]
        if self.wanted[0] < self.pos[0] and self.pos[0] not in tuple(range(self.wanted[0]-32,self.wanted[0]+32)):
            weight += [LEFT]
        if self.wanted[1] > self.pos[1] and self.pos[1] not in tuple(range(self.wanted[1]-32,self.wanted[1]+32)):
            weight += [DOWN]
        if self.wanted[1] < self.pos[1] and self.pos[1] not in tuple(range(self.wanted[1]-32,self.wanted[1]+32)):
            weight += [UP]
        next_possible1,next_possible2 = list(next_possible1),list(next_possible2)
        self.moving = (
            choice(next_possible1+weight) if self.moving[0] == None else self.moving[0],
            choice(next_possible2+weight) if self.moving[0] == None or main.loop%self.delay==0 else self.moving[1]
        )

                
class Player():
    def __init__(self,speed=1,color=(255,255,255),maxlives=3,startpos=(224,376),startface = None,width=8):
        self.pos = list(startpos)
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.speed = speed
        self.color = color
        self.width = width
        self.collision = width+1
        self.maxlives = maxlives
        self.lives = maxlives
        self.invincible = time.time()-2
        self.moving = [startface,None]
        self.history = startface
        self.dtslow = 7
    def move(self,rot,dt):
        x,y = ((0,-1),(0,1),(-1,0),(1,0))[rot]
        self.pos[0] += int(x * self.speed * (dt if dt < 30 else 30)/self.dtslow)
        self.pos[1] += int(y * self.speed * (dt if dt < 30 else 30)/self.dtslow)


if __name__ == "__main__":
    main = Main()
    while main.run:
        main.tick()
        main.logic()
        main.events()
        main.draw()
    pygame.quit()
