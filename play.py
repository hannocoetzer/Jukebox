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
from nonblocking_input import NonBlockingInput
#from chatgpt import chatgpt
from openai import OpenAI
import re
import json




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

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

def chat_with_gpt(message, model="gpt-3.5-turbo"):
    """
    Send a message to ChatGPT and get a response
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error: {str(e)}"


def chatgpt():
        # Simple chat example
    user_message = "Give me a clear list of 20 bands that is similar to " + getPlayString() + " that is of the same era or genre or style  - no bullets, no intro text, no numbers"
    response = chat_with_gpt(user_message)

    SimilarBands = process_chatgpt_list(response)

    print(f"User: {user_message}", end="\n")
    return process_chatgpt_list(response)
    
    # Example with conversation history
    def chat_with_history(messages, model="gpt-3.5-turbo"):
        """
        Chat with conversation history
        messages should be a list of {"role": "user"/"assistant", "content": "..."}
        """
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Conversation with history
    conversation = [
        {"role": "user", "content": "What's the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What's the population of that city?"}
    ]
    
    response = chat_with_history(conversation)
    print(f"\nConversation response: {response}")

def process_chatgpt_list(response_text):
    """
    Process a ChatGPT response that contains a list and clean it up
    Handles various formats: JSON arrays, comma-separated, newline-separated, numbered lists, etc.
    """

    response_text = response_text.strip()

    if response_text.startswith('[') and response_text.endswith(']'):
        try:
            items = json.loads(response_text)
            return [str(item).strip() for item in items if str(item).strip()]
        except json.JSONDecodeError:
            pass

    cleaned_text = response_text
    
    # Remove numbered list markers (1. 2. 3. etc.)
    cleaned_text = re.sub(r'^\d+\.\s*', '', cleaned_text, flags=re.MULTILINE)
    
    # Remove bullet points (•, -, *, etc.)
    cleaned_text = re.sub(r'^[•\-\*]\s*', '', cleaned_text, flags=re.MULTILINE)
    
    # Remove "Here are" type prefixes
    cleaned_text = re.sub(r'^(here are|here is|the list is|list:|items:).*?[:]\s*', '', cleaned_text, flags=re.IGNORECASE)
    
    # Split by various delimiters
    items = []
    
    # Try splitting by newlines first
    if '\n' in cleaned_text:
        items = cleaned_text.split('\n')
    # Then try commas
    elif ',' in cleaned_text:
        items = cleaned_text.split(',')
    # Finally try semicolons
    elif ';' in cleaned_text:
        items = cleaned_text.split(';')
    else:
        # If no clear delimiter, try to extract items using regex
        # Look for patterns that might be list items
        items = re.findall(r'[A-Z][^.!?]*(?:[.!?]|$)', cleaned_text)
    
    # Clean up each item
    cleaned_items = []
    for item in items:
        item = item.strip()
        
        # Remove quotes
        item = item.strip('"\'')
        
        # Remove trailing punctuation that's not part of the content
        item = re.sub(r'[,;]+$', '', item)
        
        # Skip empty items
        if item:
            cleaned_items.append(item)
    
    return cleaned_items

def startMainLoop():
    # Create NonBlockingInput ONCE at the start
    key_input = NonBlockingInput()
    key_input.start_listening()
    vlc_process = None
    current_process = None  # Define it cleanly here

    SimilarBands = []

    PlayCommand = 'Play'
    Playstring = getPlayString()
    latestPlaystring = None
    skipValue = 1
    alreadySkipped = False

    print("Key input started. Press 'd' to skip, 'q' to quit", end="\n")

    try:
        while True:
            print(PlayCommand, end="\n")
            
            if isinstance(SimilarBands, list) and SimilarBands :
                Playstring = SimilarBands[random.randint(0, min(21, len(SimilarBands)-1))]
                skipValue = random.randint(1, 15)

            command = (
                "ffmpeg -re "
                f"-i $(yt-dlp_linux "
                "--match-filter \"duration > 120\" "
                "--match-filter \"duration < 600\" "
                "--match-filter \"view_count > 300000\" "
                "--default-search ytsearch100 "
                f"--playlist-items {skipValue} "
                "-f \"bestaudio[ext=m4a]\" "
                f"-g \"{Playstring}\") "
                "-vn -c:a libmp3lame -b:a 128k -f mp3 "
                "-content_type audio/mpeg "
                "-ice_name \"My Stream\" "
                "-ice_description \"Live Stream from yt-dlp\" "
                "-ice_genre \"Rock\" "
                "-legacy_icecast 1 "
                "icecast://source:hackme@localhost:8000/stream.mp3"
            )
            #working - (stream songs)
            #command = (
            #    "yt-dlp_linux "
            #    "--match-filter \"duration > 120\" "
            #    "--match-filter \"duration < 600\" "
            #    "--match-filter \"view_count > 300000\" "    
            #    "--default-search ytsearch100 "
            #    f"--playlist-items {skipValue} "
            #    "-f \"bestaudio[ext=m4a]\" "
            #    f"-g \"{Playstring}\""
            #    " | xargs -I {} vlc {} --play-and-exit"
            #)


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
            current_process = subprocess.Popen(
                command,
                shell=True,
                preexec_fn=os.setsid
            )

            # Monitor the process
            while current_process.poll() is None:

                latestPlaystring = getPlayString()
                PlayCommand = getPlayCommand()

                if Playstring != latestPlaystring :
                    skipValue = 1
                    Playstring = latestPlaystring

                if vlc_process is None:
                    vlc_process = find_vlc_process()

                if PlayCommand == 'Skip':
                    print("\nSkipped from the browser.")
                    if vlc_process and vlc_process.is_running():
                        vlc_process.kill()
                    os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
                    SimilarBands.clear()
                    SimilarBands.append(latestPlaystring)
                    SimilarBands.extend(chatgpt())
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

    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        if current_process and current_process.poll() is None:
            current_process.terminate()
        key_input.stop()
        print("Cleaned up")

# Start the main loop
if __name__ == "__main__":
    startMainLoop()
