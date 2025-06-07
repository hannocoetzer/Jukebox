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
#global Playstring 
#global PlayCommand

conn = sqlite3.connect("play_stream.db", check_same_thread=False)
c = conn.cursor()

def getPlayString():
    c.execute("SELECT PlayString FROM posts Order by created_at DESC LIMIT 1")
    myList = c.fetchone()
    return myList[0]

def getPlayCommand():
    c.execute("SELECT PlayCommand FROM posts Order by created_at DESC LIMIT 1")
    myList = c.fetchone()
    return myList[0]


def readStream():

    while True:
        time.sleep(10)
        PlayCommand = getPlayCommand()
        Playstring = getPlayString()
        if PlayCommand == "Stop":
            subProcess.kill()

def player():
    command = "youtube-dl -o - -f \"bestaudio[filesize<100M]\" -f m4a --match-filter \"duration > 50\""
    command = command + " --min-views 50000 --playlist-start " + str(skipValue) +" \"ytsearch" + str(skipValue) + ":" + Playstring + "\" | vlc - --play-and-exit"
    command = command + ""
    subProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

#-- No of Songs to play
def startMainLoop():
   
    #Playstring = getPlayString()
    #PlayCommand = getPlayCommand()
    amount = 200

    skipValue = 20

    while amount > 0:

        time.sleep(3)

        Playstring = getPlayString()
        PlayCommand = getPlayCommand()

        #Rules
        if PlayCommand == "Skip":
            skipValue = skipValue + 1
        if PlayCommand == "Stop":
            skipValue = 10

        if PlayCommand == "Play":
            try:
                #-- Building command
                if platform == "linux" or platform == "linux2":
				    #--old faithfull VLC                        
				    #command = "youtube-dl -o - -f 'bestaudio[filesize<100M]' -f m4a --match-filter 'duration < 500'"
				    #command = command + " --min-views 100000 --playlist-start " + str(youN) +" 'ytsearch" + str(youN) + ":"+ artistToPlay + "' | cvlc - --play-and-exit"
				    #--mplayer implemenation
				    #command = "youtube-dl -o - -f 'bestaudio[filesize<100M]' -f m4a --match-filter 'duration < 500'"
				    #command = command + " --min-views 100000 --playlist-start " + str(youN) +" 'ytsearch" + str(youN) + ":"+ artistToPlay + "'"
				    #command = command + " $video | mplayer -slave -input file=/tmp/pipe -vo fbdev2 -zoom -xy 1920 -cache 30720 -cache-min 2 /dev/fd/3 3<&0 </dev/tty"
				    ##Artist + song combined Youtube search
				    #command = "youtube-dl -o - -f 'bestaudio[filesize<100M]' -f m4a --match-filter 'duration < 500' 'ytsearch:" + artistToPlay + " " + artistSongToPlay + "' | mplayer -slave -input file=/tmp/pipe -vo fbdev2 -zoom -xy 1920 -cache 30720 -cache-min 2 /dev/fd/3 3<&0 </dev/tty "

                    command = "youtube-dl -o - -f 'bestaudio[filesize<100M]' -f m4a --match-filter 'duration > 50' 'ytsearch" + skipValue + ":" + Playstring + "' | mplayer -slave -input file=/tmp/pipe -vo fbdev2 -zoom -xy 1920 -cache 30720 -cache-min 2 /dev/fd/3 3<&0 </dev/tty "
                elif platform == "win32":
                    command = "youtube-dl -o - -f \"bestaudio[filesize<100M]\" -f m4a --match-filter \"duration > 50\""
                    command = command + " --min-views 50000 --playlist-start " + str(skipValue) +" \"ytsearch" + str(skipValue) + ":" + Playstring + "\" | vlc - --play-and-exit"
                    command = command + ""
                    subProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
                    #os.system(command)
                    skipValue = skipValue + 1
            
                amount = amount - 1
            
            except Exception as e:
                print(e)
                amount = amount + 1

    startMainLoop()




#-------=================== start ===================-------#
#threading.start_new_thread(readStream, ())
t = threading.Thread(name='readStream', target=readStream)
t.start()
startMainLoop()
