from tkinter import *
from tkinter.filedialog import askopenfilename

import eyed3 as id3
from eyed3 import load

import pygame as pg
from pygame import mixer

import os.path
import random
from random import seed
import time
import threading

'''
list of known bugs:

1)shuffle only works on one song so far
2)doesn't queue the whole playlist

'''

# pygame and tkinter configure
root = Tk()
root.geometry('1100x770')
root.title("Suzie Q")
root.iconbitmap(r'favicon.ico')  # program's icon
root.configure(background='#B4A8F0')
mixer.init()  # initialize mixer
pg.init()     # initialize pygame


class Pause(object):  # toggles between pausing and unpausing the music

    def __init__(self):
        self.paused = mixer.music.get_busy()

    def toggle(self):
        if self.paused:
            if starting_song == songslist.curselection()[0]:
                mixer.music.unpause()
            else:
                mixer.music.stop()
            if mixer.music.get_busy():
                pauseBtn.place(x=540, y=700)
                playbutton.place_forget()
        if not self.paused:
            mixer.music.pause()
            if mixer.music.get_busy():
                playbutton.place(x=540, y=700)
                pauseBtn.place_forget()
        self.paused = not self.paused


PAUSE = Pause()

path_list = []  # stores the path of the songs that the user opened

starting_song = 0  # variable to keep count on which track you are


def load_songs():  # opens the "savedSongs" text file and adds them to the path_list list
    with open("savedSongs.txt", "r") as savedSongs:
        for line in savedSongs:
            path_list.append(line.strip())
            add_to_list(line)


def open_file():  # lets the user pick a song.
    Tk().withdraw()
    # Opens up the explorer so the user can select a song
    filename = askopenfilename(filetypes=[('.mp3', '*.mp3'), ('.wav', '.wav'), ('.ogg', '.ogg')])
    # adds the song address to path_list
    path_list.append(filename)
    # adds the song to show on the list box
    add_to_list(filename)
    # writes the song address to the savedSongs text file to be loaded by the user, if it doesn't exist, it will create
    # it
    with open("savedSongs.txt", "a") as savedSongs:
        savedSongs.seek(0, 2)
        savedSongs.write(filename + '\n')


def add_to_list(file):  # adds the song (file) address to show on the list box
    song = os.path.basename(file)
    songslist.insert(END, song)
    songslist.selection_set(0)
    global starting_song
    starting_song = songslist.curselection()[0]

'''
def queue_list():
    for song in path_list:
        mixer.music.load(str(song))
        mixer.music.play()
        print("Playing::::: " + song)
        while mixer.music.get_busy():
            continue
       random.shuffle(path_list)
        for song in path_list:
            mixer.music.load(str(song))
            mixer.music.play()
            print("Playing::::: " + song)
            while mixer.music.get_busy():
                pg.event.get()
                continue
                
'''


def play_song():  # starts the currently selected song and places the pause button to appear instead of the play button
    if not mixer.music.get_busy():
        pauseBtn.place(x=540, y=700)
        playbutton.place_forget()
        mixer.music.stop()
        global starting_song
        starting_song = songslist.curselection()[0]
        mixer.music.load(path_list[starting_song])
        mixer.music.set_volume(0.5)
        mixer.music.play()
    elif mixer.music.get_busy():  # if music is already playing, pause instead of playing a new song.
        PAUSE.toggle()


def duration_from_seconds(s):
    """Module to get the convert Seconds to a time like format."""
    s = s
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    timelapsed = "{:01d}:{:02d}:{:02d}:{:02d}".format(int(d),
                                                      int(h),
                                                      int(m),
                                                      int(s))
    return timelapsed


menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=open_file)
filemenu.add_command(label="Load", command=load_songs)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
root.config(menu=menubar)


def change_volume(value):
    # mixer only allows values between 0 and 1, as in "0.1", "0.2" etc. up to 1
    mixer.music.set_volume(int(value) / 100)


volume = Scale(root, orient=HORIZONTAL, length=110, from_=0, to=100,
               activebackground='#B4A8F0', background='#B4A8F0', borderwidth=0, highlightthickness=0,
               command=change_volume)  # volume bar
volume.set(50)  # sets the volume to 50% when the program starts
volume.place(x=980, y=690)

songslist = Listbox(root, height=40, width=120)  # a list that will show the loaded songs
songslist.place(x=370, y=5, bordermode=OUTSIDE)


def show_song_info(track_time):
    duration = Label(root, text=str(duration_from_seconds(track_time)),
                     bg='#B4A8F0', activebackground='#B4A8F0')
    print(mixer.music.get_pos())
    duration.place(x=1020, y=645)
    

songLength = Scale(root, orient=HORIZONTAL, length=720, from_=0, to=100, activebackground='#B4A8F0',
                   background='#B4A8F0', borderwidth=0, highlightthickness=0,
                   command=lambda *args: show_song_info(id3.load(path_list[starting_song]).info.time_secs))
songLength.set(0)
songLength.place(x=370, y=650)


def skip_song():
    global starting_song
    if starting_song == songslist.size() - 1:  # if the currently playing song is the last song
        starting_song = 0  # currently playing song index becomes 0, as in the first one in the list
        songslist.selection_clear(0, END)  # clears the selection of the list box
        songslist.selection_set(0)  # selects the first one on the first
        mixer.music.load(path_list[0])
        pauseBtn.place(x=540, y=700)
        playbutton.place_forget()
        mixer.music.play()
    else:
        mixer.music.load(path_list[starting_song + 1])  # loads the next song by increasing the value of starting_song
        songslist.selection_clear(0, END)  # clears the selection of the list box
        songslist.selection_set(starting_song + 1)
        pauseBtn.place(x=540, y=700)
        playbutton.place_forget()
        mixer.music.play()
        starting_song += 1


def change_shuffle_value(shufflevalue):  # toggles the shuffle button, work in progress.
    if shufflevalue == 1:
        shuffleButtonActive.place(x=450, y=700)
        shuffleButtonInactive.place_forget()
        shufflethread(1).start()
    elif shufflevalue == 0:
        shuffleButtonInactive.place(x=450, y=700)
        shuffleButtonActive.place_forget()
        shufflethread().start()


class shufflethread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        queue_list()


shufflethread.daemon = True




seed(1)  # I don't know why this is here. Probably for implementing "choice" so we can use it in shuffle.

# shuffle buttons #
shuffleInactiveIcon = PhotoImage(file="shuffleinactive.png")
shuffleButtonInactive = Button(root, image=shuffleInactiveIcon, borderwidth=0, activebackground='#B4A8F0',
                               background='#B4A8F0', command=lambda *args: change_shuffle_value(1))
shuffleButtonInactive.place(x=450, y=700)

shuffleActiveIcon = PhotoImage(file="shuffleactive.png")
shuffleButtonActive = Button(root, image=shuffleActiveIcon, borderwidth=0, activebackground='#B4A8F0',
                             background='#B4A8F0', command=lambda *args: change_shuffle_value(0))

repeat_value = 0


def repeat(value):
    global repeat_value
    global starting_song
    if value == 0:
        repeat_value = 0
        repeatActiveButton.place(x=620, y=700)
        repeatInactiveButton.place_forget()
        for song in path_list:
            time.sleep(id3.load(path_list[starting_song]).info.time_secs)
            mixer.music.queue(path_list[starting_song + 1])
            starting_song += 1
            if starting_song == songslist.size() - 1:
                starting_song = 0

    elif value == 1:
        repeat_value = 1
        repeatOneButton.place(x=620, y=700)
        repeatActiveButton.place_forget()
        if mixer.music.get_busy():
            mixer.music.play(-1)

    elif value == 2:
        repeat_value = 2
        repeatInactiveButton.place(x=620, y=700)
        repeatActiveButton.place_forget()
        repeatOneButton.place_forget()


def mute(muteVal):
    if not muteVal:
        global prev_volume
        prev_volume = mixer.music.get_volume()
        volume.set(0)
        mixer.music.set_volume(0)
        muteButton.place(x=930, y=700)
        volumeButton.place_forget()
    elif muteVal:
        volume.set(prev_volume*100)
        mixer.music.set_volume(prev_volume)
        volumeButton.place(x=930, y=700)
        muteButton.place_forget()


# Most Icons/buttons are on here.
volumeIcon = PhotoImage(file="volume.png")
volumeButton = Button(root, image=volumeIcon, borderwidth=0, activebackground='#B4A8F0', background='#B4A8F0',
                      command=lambda *args: mute(0))
volumeButton.place(x=930, y=700)

muteIcon = PhotoImage(file="mute.png")
muteButton = Button(root, image=muteIcon, borderwidth=0, activebackground='#B4A8F0', background='#B4A8F0',
                    command=lambda *args: mute(1))


repeatOneIcon = PhotoImage(file="repeatone.png")
repeatOneButton = Button(root, image=repeatOneIcon, borderwidth=0, activebackground='#B4A8F0', background='#B4A8F0',
                         command=lambda *args: repeat(2))

repeatInactiveIcon = PhotoImage(file="repeatInactive.png")
repeatInactiveButton = Button(root, image=repeatInactiveIcon, borderwidth=0, activebackground='#B4A8F0',
                              background='#B4A8F0', command=lambda *args: repeat(0))
repeatInactiveButton.place(x=620, y=700)

repeatActiveIcon = PhotoImage(file="repeat.png")
repeatActiveButton = Button(root, image=repeatActiveIcon, borderwidth=0, activebackground='#B4A8F0',
                            background='#B4A8F0', command=lambda *args: repeat(1))

nextIcon = PhotoImage(file="next.png")
nextbutton = Button(root, image=nextIcon, borderwidth=0, activebackground='#B4A8F0', background='#B4A8F0',
                    command=skip_song)
nextbutton.place(x=580, y=700)

playIcon = PhotoImage(file="play.png")
playbutton = Button(root, image=playIcon, borderwidth=0, activebackground='#B4A8F0', background='#B4A8F0',
                    command=play_song)
playbutton.place(x=540, y=700)

pauseIcon = PhotoImage(file="pause.png")
pauseBtn = Button(root, image=pauseIcon, borderwidth=0, activebackground='#B4A8F0', background='#B4A8F0',
                  command=play_song)

statusbar = Label(root, text=f"Now Playing: ", bd=1, relief=SUNKEN, anchor=W)
statusbar.place(x=0, y=710)


def prev_song():
    global starting_song
    if starting_song == 0:
        starting_song = songslist.size() - 1
        mixer.music.load(path_list[songslist.size() - 1])
        songslist.selection_clear(0, END)
        songslist.selection_set(END)
        pauseBtn.place(x=540, y=700)
        playbutton.place_forget()
        mixer.music.play()
    else:
        mixer.music.load(path_list[starting_song - 1])
        songslist.selection_clear(0, END)
        songslist.selection_set(starting_song - 1)
        pauseBtn.place(x=540, y=700)
        playbutton.place_forget()
        mixer.music.play()
        starting_song -= 1


backIcon = PhotoImage(file="back.png")
backbutton = Button(root, image=backIcon, borderwidth=0, activebackground='#B4A8F0', background='#B4A8F0',
                    command=prev_song)
backbutton.place(x=490, y=700)


load_songs()
root.mainloop()
