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
import psutil
import signal
from nonblocking_input import NonBlockingInput

conn = sqlite3.connect("play_stream.db", check_same_thread=False)
c = conn.cursor()

def getPlayString():
    c.execute("SELECT PlayString FROM posts Order by created_at DESC LIMIT 1")
    myList = c.fetchone()
    return myList[0]

    #with open('playnow.txt', 'r', encoding='utf-8') as file:
    #    return file.read()

def getPlayCommand():
    c.execute("SELECT PlayCommand FROM posts Order by created_at DESC LIMIT 1")
    myList = c.fetchone()
    return myList[0]
    #with open('commands.txt', 'r', encoding='utf-8') as file:
    #    return file.read()

def setPlayCommand(new_value):
    # First get the ID of the last row
    c.execute("SELECT id FROM posts Order by created_at DESC LIMIT 1")
    last_id = c.fetchone()
    c.execute("SELECT PlayCommand FROM posts Order by created_at DESC LIMIT 1")
    
    if last_id:
        c.execute(f"UPDATE posts SET PlayCommand = ? WHERE id = ?", 
                      (new_value, last_id[0]))
        conn.commit()


vlc_process = None

# Wait until VLC is launched
def find_vlc_process():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'vlc' in proc.name().lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def startMainLoop():
    # Create NonBlockingInput ONCE at the start
    key_input = NonBlockingInput()
    key_input.start_listening()
    vlc_process = None
    current_process = None  # Define it cleanly here

    PlayCommand = 'Play'
    Playstring = getPlayString()
    skipValue = 1
    amount = 200
    playListIndex = 1
    alreadySkipped = False

    print("Key input started. Press 'd' to skip, 'q' to quit")

    try:
        while True:
            print(PlayCommand)

            #working - (stream songs)
            command = (
                "yt-dlp_linux "
                "--match-filter \"duration > 120\" "
                "--min-views 50000 "
                "--default-search ytsearch100 "
                f"--playlist-items {skipValue} "
                "-f \"bestaudio[ext=m4a]\" "
                f"-g \"{Playstring}\""
                " | xargs -I {} vlc {} --play-and-exit"
            )

            #working - download songs
            # command = (
            #                "yt-dlp_linux "
            #                "--extract-audio "
            #                "--audio-format mp3 "
            #                "--match-filter \"duration > 120\" "
            #                "--min-views 50000 "
            #                "--default-search ytsearch100 "
            #                f"--playlist-items {skipValue} "
            #                "--exec \"vlc {} --play-and-exit\" "
            #                f"{Playstring}"
            # )
            #if PlayCommand in ("Play", "Stop"):
            print(f"Playing: {command}")
            current_process = subprocess.Popen(
                command,
                shell=True,
                preexec_fn=os.setsid
            )

            # Monitor the process
            while current_process.poll() is None:
                Playstring = getPlayString()
                PlayCommand = getPlayCommand()


                if vlc_process is None:
                    vlc_process = find_vlc_process()

                if PlayCommand == 'Skip':
                    print("Skipped from the browser.")
                    if vlc_process and vlc_process.is_running():
                        vlc_process.kill()
                    os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
                    skipValue += 1
                    setPlayCommand('Play')
                    break

                if key_input.has_key():
                    key = key_input.get_key()
                    print(f"\nKey during playback: {key}")
                    if key == 'd' or key == 'q' or PlayCommand == 'Skip':
                        print("Terminating playback.")
                        if vlc_process and vlc_process.is_running():
                            vlc_process.kill()
                        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
                        if key == 'q':
                            return
                        skipValue += 1
                        setPlayCommand('Play')
                        break
                time.sleep(0.1)

            skipValue += 1
            amount -= 1

    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        if current_process and current_process.poll() is None:
            current_process.terminate()
        key_input.stop()
        print("Cleaned up")

def playStuff(Playstring, q):
    skipValue = 5
    command = ("yt-dlp -o - -f \"m4a[filesize<100M]/m4a\" "
             "--match-filter \"duration > 120\" --min-views 50000 "
             f"\"ytsearch{skipValue}:{Playstring}\" | "
             "\"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe\" - --play-and-exit")
    print(command)
    subie = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    q.put(subie)

# Start the main loop
if __name__ == "__main__":
    startMainLoop()
