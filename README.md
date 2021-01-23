# Music Folder Player (macOS, afplay + caffeinate)

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Advanced Usage](#advanced-usage)

## Description

This program provides convenient text interface wrapper for using afplay, the built-in high quality
macOS music file player. It also uses caffeinate to suppress computer idle-mode.

## Installation

To install the app, simply copy `mp3folderplayer.py` to your user folder `~`.

## Usage

To run the app, simply type the following in your Terminal app:
```
$ python3 ~/mp3folderplayer.py ~/path/to/file1 ~/path/to/file2
```
Where the arguments are paths to folders where your music is. This program accepts nested folders.

### Advanced Usage

When the program is started, type h for help. It will provide you the short list with brief description of the main functions:
```
    h -- display help info.

    pr -- previous track. Plays the previous track in the queue.
    [enter]/no input -- play the next track in the queue.

    p -- pause playback and start with the next track. The program doesn't allow to pause music in the middle which provides a continuous music experience.
    s -- silence playback. Silences the music until Enter is pressed.

    sh -- shuffle playlist. Shuffles the queue
    srt -- sort playlist. Sorts the queue

    f -- finish playing. Finish playing and exit the program
```