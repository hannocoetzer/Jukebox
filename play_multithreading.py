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
import random
import requests
from requests.auth import HTTPBasicAuth
from nonblocking_input import NonBlockingInput

# from chatgpt import chatgpt
from openai import OpenAI
import re
import json
from multiprocessing import Process


conn = sqlite3.connect("play_stream.db", check_same_thread=False)
# conn.open()


def getPlayString():
    cursor = conn.cursor()
    cursor.execute("SELECT PlayString FROM posts Order by created_at DESC LIMIT 1")
    myList = cursor.fetchone()
    cursor.close()
    return myList[0]

    # with open('playnow.txt', 'r', encoding='utf-8') as file:
    #    return file.read()


def getPlayCommand():
    cursor = conn.cursor()
    cursor.execute("SELECT PlayCommand FROM posts Order by created_at DESC LIMIT 1")
    myList = cursor.fetchone()
    cursor.close()
    return myList[0]
    # with open('commands.txt', 'r', encoding='utf-8') as file:
    #    return file.read()


def setPlayCommand(new_value):
    # First get the ID of the last row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM posts Order by created_at DESC LIMIT 1")
    last_id = cursor.fetchone()
    cursor.execute("SELECT PlayCommand FROM posts Order by created_at DESC LIMIT 1")

    if last_id:
        cursor.execute(
            f"UPDATE posts SET PlayCommand = ? WHERE id = ?", (new_value, last_id[0])
        )
        conn.commit()

    cursor.close()


def setPlayString(new_value):
    # First get the ID of the last row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM posts Order by created_at DESC LIMIT 1")
    last_id = cursor.fetchone()
    cursor.execute("SELECT PlayString FROM posts Order by created_at DESC LIMIT 1")

    if last_id:
        cursor.execute(
            f"UPDATE posts SET PlayString= ? WHERE id = ?", (new_value, last_id[0])
        )
        conn.commit()

    cursor.close()


def setPlayDetails(title, duration, streamUrl):
    # First get the ID of the last row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM posts Order by created_at DESC LIMIT 1")
    last_id = cursor.fetchone()
    cursor.execute("SELECT PlayCommand FROM posts Order by created_at DESC LIMIT 1")

    if last_id:
        cursor.execute(
            f"UPDATE posts SET title = ?,duration = ?, streamUrl = ? WHERE id = ?",
            (title, duration, streamUrl, last_id[0]),
        )
        conn.commit()

    cursor.close()


vlc_process = None


# Wait until VLC is launched
def find_vlc_process():
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if "vlc" in proc.name().lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def chat_with_gpt(message, model="gpt-3.5-turbo"):
    """
    Send a message to ChatGPT and get a response
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


def chatgpt():
    # Simple chat example
    user_message = (
        "Give me a clear list of 20 bands that is similar to "
        + getPlayString()
        + " that is of the same era or genre or style  - no bullets, no intro text, no numbers"
    )
    response = chat_with_gpt(user_message)

    SimilarBands = process_chatgpt_list(response)

    print(f"User: {user_message}", end="\n")
    return process_chatgpt_list(response)


def process_chatgpt_list(response_text):
    """
    Process a ChatGPT response that contains a list and clean it up
    Handles various formats: JSON arrays, comma-separated, newline-separated, numbered lists, etc.
    """

    response_text = response_text.strip()

    if response_text.startswith("[") and response_text.endswith("]"):
        try:
            items = json.loads(response_text)
            return [str(item).strip() for item in items if str(item).strip()]
        except json.JSONDecodeError:
            pass

    cleaned_text = response_text

    # Remove numbered list markers (1. 2. 3. etc.)
    cleaned_text = re.sub(r"^\d+\.\s*", "", cleaned_text, flags=re.MULTILINE)

    # Remove bullet points (•, -, *, etc.)
    cleaned_text = re.sub(r"^[•\-\*]\s*", "", cleaned_text, flags=re.MULTILINE)

    # Remove "Here are" type prefixes
    cleaned_text = re.sub(
        r"^(here are|here is|the list is|list:|items:).*?[:]\s*",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    # Split by various delimiters
    items = []

    # Try splitting by newlines first
    if "\n" in cleaned_text:
        items = cleaned_text.split("\n")
    # Then try commas
    elif "," in cleaned_text:
        items = cleaned_text.split(",")
    # Finally try semicolons
    elif ";" in cleaned_text:
        items = cleaned_text.split(";")
    else:
        # If no clear delimiter, try to extract items using regex
        # Look for patterns that might be list items
        items = re.findall(r"[A-Z][^.!?]*(?:[.!?]|$)", cleaned_text)

    # Clean up each item
    cleaned_items = []
    for item in items:
        item = item.strip()

        # Remove quotes
        item = item.strip("\"'")

        # Remove trailing punctuation that's not part of the content
        item = re.sub(r"[,;]+$", "", item)

        # Skip empty items
        if item:
            cleaned_items.append(item)

    return cleaned_items


similarArtists = []
title = ""
duration = 999999


def startMainLoop():
    key_input = NonBlockingInput()
    key_input.start_listening()
    global similarArtists

    setPlayCommand("Play")

    print("Key input started. Press 'd' to skip, 'q' to quit", end="\n")
    Playstring = getPlayString()

    similarArtists = chatgpt()

    streamNum = 1
    setPlayCommand("Play")

    manager = IcecastManager()
    manager.start_stream(streamNum)

    try:
        while True:
            skipDetected = False

            latestPlaystring = getPlayString()
            PlayCommand = getPlayCommand()

            if key_input.has_key():
                key = key_input.get_key()
                if key == "q":
                    break

            if Playstring != latestPlaystring:
                Playstring = latestPlaystring
                setPlayString(Playstring)
                # skipValue = 1
                setPlayCommand("Skip")
                skipDetected = True

            if PlayCommand == "Skip":
                print("\nSkipped from the browser.")
                similarArtists = chatgpt()
                setPlayCommand("Skip")
                skipDetected = True

            if key_input.has_key():
                key = key_input.get_key()
                print(f"\nKey during playback: {key}")
                if key == "d" or key == "q" or PlayCommand == "Skip":
                    print("Terminating playback.")

                    if key == "q":
                        break

                    setPlayCommand("Skip")
                    skipDetected = True

            if skipDetected:
                setPlayCommand("Play")
                streamNum = 1 if streamNum == 2 else 2
                manager.start_stream(streamNum)

            time.sleep(0.2)

    except KeyboardInterrupt:
        os._exit(1)
    finally:
        os._exit(1)


def GetSongDetail(Playstring, skipValue):
    global duration
    global title
    print(Playstring)
    print(skipValue)
    command = [
        "yt-dlp_linux",
        "--match-filter",
        "duration > 120",
        "--match-filter",
        "duration < 600",
        "--match-filter",
        "view_count > 300000",
        "--default-search",
        "ytsearch100",
        "--playlist-items",
        str(skipValue),  # 👈 safer and clearer
        "--simulate",
        "--print",
        "%(title)s - %(duration)s seconds",
        Playstring,
    ]

    result = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # or use `universal_newlines=True` if using older Python
    )
    stdout, stderr = result.communicate()

    output = stdout.strip()

    match = re.match(r"(.+?)\s+-\s+(\d+)\s+seconds", output)
    if match:
        title = match.group(1)

        duration = int(match.group(2))
        # setTitleAndDuration(title, duration)
        print("Title:", title)
        print("Seconds:", duration)

        return title, duration
    else:
        print("No match found in output.")


class IcecastStreamThread(threading.Thread):
    def __init__(self, streamNum):
        global similarArtists
        super().__init__()
        self.streamNum = streamNum
        self.process = None
        self._stop_event = threading.Event()
        self.daemon = True  # Dies with main program
        self.skipValue = random.randint(1, 15)
        self.playstring = getPlayString()

        if similarArtists:
            self.playstring = similarArtists[random.randint(1, 20)]

        self.title, self.duration = GetSongDetail(self.playstring, self.skipValue)
        self.streamUrl = f"localhost:8000/stream{str(self.streamNum)}.mp3"
        setPlayDetails(self.title, self.duration, "http://" + self.streamUrl)

    def run(self):
        try:
            self.command = (
                "ffmpeg -re "
                f"-i $(yt-dlp_linux "
                '--match-filter "duration > 120" '
                '--match-filter "duration < 600" '
                '--match-filter "view_count > 300000" '
                "--default-search ytsearch100 "
                f"--playlist-items {self.skipValue} "
                '-f "bestaudio[ext=m4a]" '
                f'-g "{self.playstring}") '
                "-vn -c:a libmp3lame -b:a 128k -f mp3 "
                "-content_type audio/mpeg "
                '-ice_name "My Stream" '
                '-ice_description "Live Stream from yt-dlp" '
                '-ice_genre "Rock" '
                "-legacy_icecast 1 "
                f"icecast://source:hackme@localhost:8000/stream{str(self.streamNum)}.mp3"
            )

            self.process = subprocess.Popen(
                self.command, shell=True, preexec_fn=os.setsid
            )

            # Monitor the process while checking for stop signal
            while not self._stop_event.is_set():
                if self.process.poll() is not None:
                    # Process ended naturally
                    break
                time.sleep(0.1)  # Check every 100ms

        except Exception as e:
            print(f"Error in stream thread: {e}")
        finally:
            self._cleanup()

    def stop(self):
        self._stop_event.set()
        self._cleanup()

    def _cleanup(self):
        if self.process and self.process.poll() is None:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.wait()

            except (ProcessLookupError, OSError):
                # Process already dead
                pass


class IcecastManager:
    def __init__(self):
        self.current_stream = None

    def start_stream(self, streamNum):
        if self.current_stream and self.current_stream.is_alive():
            self.stop_current_stream()

        # Start new stream
        self.current_stream = IcecastStreamThread(streamNum)
        self.current_stream.start()
        print("New icecast stream started")

    def stop_current_stream(self):
        if self.current_stream:
            self.current_stream.stop()
            self.current_stream.join(timeout=5)  # Wait up to 5 seconds

            if self.current_stream.is_alive():
                print("Warning: Thread didn't stop gracefully")
            else:
                print("Stream stopped successfully")


# Start the main loop
if __name__ == "__main__":
    startMainLoop()
