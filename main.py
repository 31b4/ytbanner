from datetime import date
from PIL import Image, ImageDraw, ImageFont
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Configuration
WIDTH, HEIGHT = 2560, 1440
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_PICKLE = 'token.pickle'
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def generate_banner(progress, total_days):
    img = Image.new('RGB', (WIDTH, HEIGHT), color='black')
    draw = ImageDraw.Draw(img)
    # Draw progress bar
    progress_width = int((progress / total_days) * WIDTH * 0.8)
    bar_x1, bar_y1 = WIDTH * 0.1, HEIGHT // 2
    bar_x2, bar_y2 = bar_x1 + progress_width, bar_y1 + 40
    draw.rectangle([bar_x1, bar_y1, WIDTH * 0.9, bar_y2], fill="gray")
    draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill="white")
    img.save("youtube_banner.png")

def update_youtube_banner():
    # Load credentials
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    # Initialize API
    youtube = build("youtube", "v3", credentials=creds)
    # Upload banner
    request = youtube.channelBanners().insert(
        media_body="youtube_banner.png"
    )
    response = request.execute()
    print("Banner updated:", response)

if __name__ == "__main__":
    today = date.today()
    current_day = today.timetuple().tm_yday
    total_days = 365 if today.year % 4 != 0 else 366
    generate_banner(current_day, total_days)
    update_youtube_banner()