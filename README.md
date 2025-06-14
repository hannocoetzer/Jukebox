# PyPlayer
Stream high quality audio from Youtube

*Requirements*
Python 3.13.2
VLC
FFMPEG

*Executing*
edit > playnow.txt
run > python3 play.py

*Linux*
sudo apt install python3
sudo apt install pip
sudo apt install python3-psutil

*Running from browser*
sudo apt install apache2 php libapache2-mod-php php-sqlite3 php-pdo-sqlite
cd /PyPlayer
php -S localhost:8080
python3 play.py
browse to http://localhost:8080/play.html

*Smart randomized playlist*
pip install openai
export OPENAI_API_KEY="your key"
sudo apt install pipx
pipx install openai
or
install openai --break-system-packages

*Local radio setup with Streaming to browser with icecast2*
sudo apt install icecast2
sudo nano /etc/icecast2/icecast.xml
<listen-socket>
  <port>8000</port>
  <bind-address>0.0.0.0</bind-address>
</listen-socket>

sudo systemctl restart icecast2

F*urther reading and optimisation*

https://github.com/yt-dlp/yt-dlp
