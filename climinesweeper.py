import curses
import cursesplus
from curses.textpad import rectangle
import sys
import os
import random
from time import sleep
import datetime
from eptranslate import *

#GAME_X_SIZE = 10
#GAME_Y_SIZE = 10
#MINES = 10

def gen_2d_array(xs,yx,prefill) -> list[list]:
    final = []
    for x in range(xs):
        tf = []
        for y in range(yx):
            tf.append(prefill)
        final.append(tf)
    return final

def collapse_2d_array(ar) -> list:
    final = []
    for a in ar:
        for b in a:
            final.append(b)
    return final

def is_coord_in_array(ar,x,y) -> bool:
    f = True
    if x < 0 or y < 0:
        f = False
    else:
        try:
            ar[x][y]
        except:
            f = False
    return f

def get_nearby(ar,x,y):
    fn = []
    for lx in range(x-1,x+2):
        for ly in range(y-1,y+2):
            if is_coord_in_array(ar,lx,ly):
                if ar[lx][ly]:
                    fn.append(True)
                else:
                    fn.append(False)
            else:
                fn.append(False)
    return fn

cols_list = [cursesplus.BLACK,cursesplus.BLUE,cursesplus.GREEN,cursesplus.YELLOW,cursesplus.RED,cursesplus.MAGENTA,cursesplus.constants.CYAN,cursesplus.WHITE,cursesplus.WHITE,cursesplus.WHITE]

def sc_wrapper(bg,fg,invert=False):
    if not invert:
        return cursesplus.set_colour(bg,fg)
    else:
        return cursesplus.set_colour(fg,bg)

def cl_ls(ar):
    return len([g for g in ar if g])

def rechighlight(x,y,MINE_ARRAY,SHOW_ARRAY):

    for nx in range(x-1,x+2):
        for ny in range(y-1,y+2):
            if is_coord_in_array(SHOW_ARRAY,nx,ny) and not SHOW_ARRAY[nx][ny]:
                SHOW_ARRAY[nx][ny] = True
                if cl_ls(get_nearby(MINE_ARRAY,nx,ny)) == 0:
                    rechighlight(nx,ny,MINE_ARRAY,SHOW_ARRAY)

def game(stdscr,GAME_X_SIZE,GAME_Y_SIZE,MINES,title="Minesweeper"):
    cursesplus.utils.hidecursor()
    stdscr.nodelay(1)
    MINE_ARRAY = gen_2d_array(GAME_X_SIZE,GAME_Y_SIZE,False)
    GAME_ARRAY = gen_2d_array(GAME_X_SIZE,GAME_Y_SIZE,0)
    SHOW_ARRAY = gen_2d_array(GAME_X_SIZE,GAME_Y_SIZE,False)
    FLAG_ARRAY = gen_2d_array(GAME_X_SIZE,GAME_Y_SIZE,False)
    for i in range(MINES):
        while True:
            rx = random.randint(0,GAME_X_SIZE-1)
            ry = random.randint(0,GAME_Y_SIZE-1)
            if MINE_ARRAY[rx][ry]:
                continue
            MINE_ARRAY[rx][ry] = True
            break

    xl = 0
    yl = 0
    for col in MINE_ARRAY:
        for obj in col:
            
            if MINE_ARRAY[xl][yl]:
                GAME_ARRAY[xl][yl] = 9
            else:
                GAME_ARRAY[xl][yl] = len([g for g in get_nearby(MINE_ARRAY,xl,yl) if g])

            yl += 1
        xl += 1
        yl = 0

    starttime = datetime.datetime.now()
    curs_x = 1
    curs_y = 1
    winable = True
    while True:
        stdscr.clear()
        rectangle(stdscr,0,0,GAME_Y_SIZE+1,GAME_X_SIZE+1)
        stdscr.addstr(GAME_Y_SIZE+2,0,f"Mines: {MINES}")
        stdscr.addstr(GAME_Y_SIZE+3,0,f"Flags: {cl_ls(collapse_2d_array(FLAG_ARRAY))}")
        #stdscr.addstr(0,10,)
        xl = 0
        yl = 0
        for col in GAME_ARRAY:
            xl += 1
            for obj in col:
                yl += 1
                if SHOW_ARRAY[xl-1][yl-1]:
                    
                    stdscr.addstr(yl,xl,str(obj),sc_wrapper(cursesplus.BLACK,cols_list[obj],yl==curs_y and xl==curs_x))
                    if obj == 0 and yl==curs_y and xl==curs_x:
                        stdscr.addstr(curs_y,curs_x,"█")
                else:
                    stdscr.addstr(yl,xl,"?",sc_wrapper(cursesplus.BLACK,cursesplus.WHITE,yl==curs_y and xl==curs_x))
                if FLAG_ARRAY[xl-1][yl-1]:
                    stdscr.addstr(yl,xl,"F",sc_wrapper(cursesplus.RED,cursesplus.WHITE,yl==curs_y and xl==curs_x))
            yl = 0
        
        #stdscr.addstr(curs_y+1,curs_x+1,"█")

        #stdscr.addstr(0,0,f"X: {curs_x}, Y: {curs_y}")
        dt = (datetime.datetime.now() - starttime).total_seconds()
        stdscr.addstr(GAME_Y_SIZE+1,0,f"{str(round(dt // 3600 // 1)).zfill(1)}:{str(round(dt % 3600 // 60 // 1)).zfill(2)}:{str(round(dt % 60,1)).zfill(4)}")
        stdscr.addstr(0,0,title)
        stdscr.refresh()
        k = stdscr.getch()
        if (k == curses.KEY_DOWN and curs_y < GAME_Y_SIZE):
            curs_y += 1
        elif k == curses.KEY_UP and curs_y > 1:
            curs_y -= 1
        elif k == curses.KEY_LEFT and curs_x > 1:
            curs_x -= 1
        elif k == curses.KEY_RIGHT and curs_x < GAME_X_SIZE:
            curs_x += 1
        elif k == 32 and not SHOW_ARRAY[curs_x-1][curs_y-1]:
            SHOW_ARRAY[curs_x-1][curs_y-1] = True
            if GAME_ARRAY[curs_x-1][curs_y-1] == 0:
                rechighlight(curs_x-1,curs_y-1,MINE_ARRAY,SHOW_ARRAY)
            if GAME_ARRAY[curs_x-1][curs_y-1] == 9:
                cursesplus.messagebox.showinfo(stdscr,["You died!"])
                break
        elif k == 102:
            FLAG_ARRAY[curs_x-1][curs_y-1] = not FLAG_ARRAY[curs_x-1][curs_y-1]
            SHOW_ARRAY[curs_x-1][curs_y-1] = not SHOW_ARRAY[curs_x-1][curs_y-1]
        
        elif k == 99:
            winable = False
            SHOW_ARRAY = gen_2d_array(GAME_X_SIZE,GAME_Y_SIZE,True)
            SHOW_ARRAY[0][0] = False#Cop-out to prevent win detector
        elif k == 113:
            break
            
        if cl_ls(collapse_2d_array(SHOW_ARRAY)) == GAME_X_SIZE*GAME_Y_SIZE:
            if winable:#Has the user cheated by pressing the emergency C key?
                cursesplus.messagebox.showinfo(stdscr,["You win!"])
            break
        sleep(1/100)
    cursesplus.utils.showcursor()
    stdscr.nodelay(0) 

difficulties = {
    "Easy" : {
        "x" : 10,
        "y" : 10,
        "m" : 10
    },
    "Medium" : {
        "x" : 20,
        "y" : 20,
        "m" : 25
    },
    "Hard" : {
        "x" : 50,
        "y" : 20,
        "m" : 40
    },
    "Insane" : {
        "x" : 110,
        "y" : 26,
        "m" : 400
    },
    "Super Easy" : {
        "x" : 5,
        "y" : 5,
        "m" : 2
    }
}

def menu(stdscr):
    sys.setrecursionlimit(10000)
    while True:
        wtd = cursesplus.coloured_option_menu(stdscr,["Play","Quit"],"CLISWEEPER",[["quit",cursesplus.RED]],"(c) 2024 Enderbyte Programs")
        if wtd == 1:
            break
        elif wtd == 0:
            diff = cursesplus.coloured_option_menu(stdscr,["Back","CUSTOM"]+list(difficulties.keys()),"Choose a difficulty")
            if diff == 0:
                continue
            elif diff == 1:
                try:
                    game(stdscr,
                     cursesplus.numericinput(stdscr,"X size?"),
                     cursesplus.numericinput(stdscr,"Y size?"),
                     cursesplus.numericinput(stdscr,"Mine count?"),
                     "Minesweeper - Custom")
                except Exception as e:
                    cursesplus.messagebox.showerror(stdscr,["Error",str(e)])
            else:
                diff -= 2
                dd = list(difficulties.values())[diff]
                try:
                    game(stdscr,dd["x"],dd["y"],dd["m"],"Minesweeper - "+list(difficulties.keys())[diff]+"")
                except Exception as e:
                    cursesplus.messagebox.showerror(stdscr,["Error",str(e)])

def main(stdscr):
    menu(stdscr)

curses.wrapper(main)