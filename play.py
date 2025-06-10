#useful links
#http://stackoverflow.com/questions/28416238/how-to-stop-mplayer-playing-through-python

#this really works like a charm for controlling mplayer
#http://stackoverflow.com/questions/16999865/run-mplayer-playlist-from-a-python-script

#Todo
#able to skip songs
#Lite Sql for python to save
# 1)disliked songs
# 2)favorate songs
# 3)Build similar list on the go


from sys import platform
import random
import subprocess
import time
import os, sys
import datetime
import sqlite3
import uuid
import json
import unicodedata
import threading
import sys
import queue
#global Playstring 
#global PlayCommand

conn = sqlite3.connect("play_stream.db", check_same_thread=False)
c = conn.cursor()

def getPlayString():
#    c.execute("SELECT PlayString FROM posts Order by created_at DESC LIMIT 1")
#    myList = c.fetchone()
#    return myList[0]
    with open('playnow.txt', 'r', encoding='utf-8') as file:
        return file.read()

def getPlayCommand():
    #c.execute("SELECT PlayCommand FROM posts Order by created_at DESC LIMIT 1")
    #myList = c.fetchone()
    #return myList[0]
    with open('commands.txt', 'r', encoding='utf-8') as file:
        return file.read()


def readStream():

    while True:
        time.sleep(10)
        PlayCommand = getPlayCommand()
        Playstring = getPlayString()
        if PlayCommand == "Stop":
            subProcess.kill()

def player():
    #command = "youtube-dl -o - -f \"bestaudio[filesize<100M]\" -f m4a --match-filter \"duration > 50\""
    #command = command + " --min-views 50000 --playlist-start " + str(skipValue) +" \"ytsearch" + str(skipValue) + ":" + Playstring + "\" | vlc - --play-and-exit"
    #command = command + ""
    subProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

#-- No of Songs to play
def startMainLoop():
   
    amount = 200
    playListIndex = 1

    skipValue = 20

    while amount > 0:

        time.sleep(3)
        q = queue.Queue()

        Playstring = getPlayString()
        PlayCommand = getPlayCommand()

        #Rules
        if PlayCommand == "Skip":
            skipValue = skipValue + 1
        if PlayCommand == "Stop":
            skipValue = 2

        if PlayCommand == "Play" or PlayCommand == "Stop":
            try:
                #-- Building command
                if platform == "linux" or platform == "linux2":
                    #command = "youtube-dl -o - -f 'bestaudio[filesize<100M]' -f m4a --match-filter 'duration > 50' 'ytsearch" + skipValue + ":" + Playstring + "' | mplayer -slave -input file=/tmp/pipe -vo fbdev2 -zoom -xy 1920 -cache 30720 -cache-min 2 /dev/fd/3 3<&0 </dev/tty "
                    
                    #command = "yt-dlp_linux -o - -f \"m4a[filesize<100M]/m4a\" " \
          #+ "--match-filter \"duration > 120\" --min-views 50000 " \
          #+ "\"ytsearch" + str(skipValue) + ":" + Playstring + "\" | " \
          #+ "\"mplayer\" - --play-and-exit"
                    #command = "yt-dlp_linux --extract-audio "\
                    #            + " --audio-format mp3 "\
                    #            + " --match-filter duration > 120"\
                    #            + " --min-views 50000 "\
                    #            + " --default-search ytsearch" + str(skipValue) + ""\
                    #            + " --exec vlc {} --play-and-exit "\
                    #            + Playstring
                    # "yt-dlp_linux --extract-audio --audio-format mp3 --match-filter "duration > 120" --min-views 50000 --default-search ytsearch5 --exec "vlc {} --play-and-exit" "nirvana" 
                    command = (
                                    "yt-dlp_linux "
                                    "--extract-audio "
                                    "--audio-format mp3 "
                                    "--match-filter \"duration > 120\" "
                                    "--min-views 50000 "
                                    f"--default-search ytsearch{skipValue} "
                                    "--exec \"vlc {} --play-and-exit\" "
                                    f"{Playstring}"
                                )
                    print(command)
                    subprocess.run(command, shell=True)


                
                elif platform == "win32":
                    command = "youtube-dl -o - -f \"bestaudio[filesize<100M]\" -f m4a --match-filter \"duration > 50\""
                    command = command + " --min-views 50000 --playlist-start " + str(skipValue) +" \"ytsearch" + str(skipValue) + ":" + Playstring + "\" | vlc - --play-and-exit"
                    command = "yt-dlp -o - -f \"m4a[filesize<100M]/m4a\" " \
          + "--match-filter \"duration > 120\" --min-views 50000 " \
          + "\"ytsearch" + str(skipValue) + ":" + Playstring + "\" | " \
          + "\"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe\" - --play-and-exit"


                    try:
                        if t.is_alive() == True:
                            if PlayCommand == "Stop":
                                result = q.get()
                            #t = threading.Thread(target=playStuff, args=(Playstring,))
                            #t.start()
                    except Exception as e:
                            t = threading.Thread(target=playStuff, args=(Playstring,q))
                            t.start()

                    skipValue = skipValue + 1
            
                amount = amount - 1
            
            except Exception as e:
                print(e)
                amount = amount + 1

    startMainLoop()


class MyClass(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        skipValue = 2
        Playstring = "Indie music"
        command = command = "yt-dlp -o - -f \"m4a[filesize<100M]/m4a\" " \
          + "--match-filter \"duration > 120\" --min-views 50000 " \
          + "\"ytsearch" + str(skipValue) + ":" + Playstring + "\" | " \
          + "\"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe\" - --play-and-exit"
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
        #p = subprocess.Popen(command,
        #                     shell=False,
        #                     stdout=subprocess.PIPE,
        #                     stderr=subprocess.PIPE)

        self.stdout, self.stderr = p.communicate()

def playStuff(Playstring, q):
        skipValue = 5
        command = command = "yt-dlp -o - -f \"m4a[filesize<100M]/m4a\" " \
          + "--match-filter \"duration > 120\" --min-views 50000 " \
          + "\"ytsearch" + str(skipValue) + ":" + Playstring + "\" | " \
          + "\"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe\" - --play-and-exit"
        print(command);
        subie = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        q.put(subie)

#-------=================== start ===================-------#
#threading.start_new_thread(readStream, ())
#t = threading.Thread(name='readStream', target=readStream)
#t.start()
startMainLoop()
