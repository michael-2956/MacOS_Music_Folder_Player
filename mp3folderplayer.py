"""
This program plays all the music in the folder and its subfolders.

Usage:
python3 ~/path/to/mp3folderplayer.py ~/path/to/folder1 ~/path/to/folder2

While running you can use multiple functions, to see them just type h.
"""
import sys
from os import walk
from random import shuffle
from os.path import join, basename
from subprocess import Popen, PIPE
from signal import SIGSTOP, SIGCONT
from threading import Thread, Event

state = None
STATE_PLAYING = 0
STATE_FINISHED = 1
STATE_TERMINATED_PREVIOUS = 2
STATE_TERMINATED = 3
STATE_TERMINATED_PAUSED = 4
STATE_TERMINATED_FINISH = 5
STATE_SHUFFLE_PLAYLIST = 6
STATE_SORT_PLAYLIST = 7
STATE_SILENCE = 8

command_dict = {
    "" : STATE_TERMINATED,
    "pr" : STATE_TERMINATED_PREVIOUS,
    "p" : STATE_TERMINATED_PAUSED,
    "f" : STATE_TERMINATED_FINISH,
    "sh" : STATE_SHUFFLE_PLAYLIST,
    "srt" : STATE_SORT_PLAYLIST,
    "s" : STATE_SILENCE
}

HELP_MSG = """
Help:
    h -- display help info

    pr -- previous track
    [enter]/no input -- next track

    p -- pause playback and start with the next track
    s -- silence playback

    sh -- shuffle playlist
    srt -- sort playlist

    f -- finish playing
"""

should_process_state = Event()

playing_process = None

def listallfiles_indir(path):
    """
    Walks through all the files in directory and its subdirectories and returns them.
    """
    # root, directories, files
    for root, _, files in walk(path):
        for file in files:
            yield join(root, file)


def play(filename):
    """
    Plays the music file in playing_process.
    Sets should_process_state when finished.
    """
    global state
    global should_process_state
    global playing_process

    state = STATE_PLAYING
    print("\r" + basename(filename), flush=True)

    playing_process = Popen(["caffeinate", "-i", "afplay", filename], stdout=PIPE, stderr=PIPE)
    playing_process.wait()

    state = STATE_FINISHED

    should_process_state.set()


def play_terminate():
    """
    Terminates current audio and waits for it to terminate
    """
    global playing_process
    playing_process.terminate()
    playing_process.wait()


def input_wait():
    """
    Waits for the new input
    """
    global state
    global should_process_state
    global command_dict

    while True:
        i = input()
        if i == "h":
            print(HELP_MSG, end='\n>>> ')
        elif i in command_dict:
            state = command_dict[i]
            break
        else:
            print("Command not recognised. Type h for help.", end='\n>>> ')

    should_process_state.set()


def main(paths: list):
    """
    This main funciton. Plays all the music in given files
    """
    global state
    global should_process_state
    global playing_process

    print("Scanning folders... ", end='')
    musicfiles = []
    for path in paths:
        musicfiles += [
            file for file in listallfiles_indir(path)
            if any([file.endswith(ending) for ending in [
                ".wav", ".mp3", "aiff", ".ogg", ".m4a", "flac"
            ]])
        ]
    file_num = 0
    musicfiles.sort()
    print('\r' + ' ' * 20, end='')

    t_play, t_inp = None, None

    create_new_t_play = True
    create_new_t_inp = True

    while True:
        if file_num >= len(musicfiles):
            break
        file = musicfiles[file_num]

        if create_new_t_play:
            t_play = Thread(target = play, args =(file, ))
        if create_new_t_inp:
            t_inp = Thread(target = input_wait)

        should_process_state.clear()
        if create_new_t_play:
            t_play.start()
        if create_new_t_inp:
            t_inp.start()

        print(end='>>> ', flush=True)
        should_process_state.wait()

        create_new_t_play = True
        create_new_t_inp = True
        if state == STATE_FINISHED:
            print()
            file_num += 1
            # do not create a new one if an old one is still waiting for input
            create_new_t_inp = False
        elif state == STATE_TERMINATED:
            file_num += 1
            play_terminate()
        elif state == STATE_TERMINATED_PAUSED:
            file_num += 1
            play_terminate()
            input("Press Enter to unpause.")
        elif state == STATE_TERMINATED_PREVIOUS:
            file_num -= 1
            play_terminate()
        elif state == STATE_TERMINATED_FINISH:
            play_terminate()
            break
        elif state == STATE_SHUFFLE_PLAYLIST:
            file_num = 0
            shuffle(musicfiles)
            # do not start playing new track if shuffle signal was sent
            create_new_t_play = False
        elif state == STATE_SORT_PLAYLIST:
            file_num = 0
            musicfiles.sort()
            # do not start playing new track if sort signal was sent
            create_new_t_play = False
        elif state == STATE_SILENCE:
            playing_process.send_signal(SIGSTOP)
            input("Press Enter to unsilence.")
            playing_process.send_signal(SIGCONT)
            # do not start playing new track if silence signal was sent
            create_new_t_play = False
        else:
            # will never happen
            print(f"Invalid {state = }!", flush = True)
            play_terminate()
            break

        state = -1


if __name__ == "__main__":
    main(list(sys.argv[1:]))
