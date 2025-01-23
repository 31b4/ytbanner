from datetime import date
from PIL import Image, ImageDraw, ImageFont
import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Configuration
WIDTH, HEIGHT = 2560, 1440
TOKEN_PICKLE = 'token.pickle'
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Save JSON credentials from GitHub secret to a temporary file
CLIENT_SECRET_JSON = os.environ.get("GOOGLE_CREDENTIALS")
if CLIENT_SECRET_JSON is None:
    raise EnvironmentError("Missing GOOGLE_CREDENTIALS environment variable")

TEMP_SECRET_FILE = 'client_secret.json'
with open(TEMP_SECRET_FILE, 'w') as f:
    json.dump(json.loads(CLIENT_SECRET_JSON), f)

def generate_banner(progress, total_days):
    img = Image.new('RGB', (WIDTH, HEIGHT), color='black')
    draw = ImageDraw.Draw(img)

    # Define bar dimensions and radius for rounded corners
    bar_x1, bar_y1 = WIDTH * 0.1, HEIGHT // 2
    bar_x2, bar_y2 = WIDTH * 0.9, bar_y1 + 40
    radius = 20  # Adjust the corner radius here

    # Draw background bar (gray, with rounded corners)
    draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=radius, fill="gray")

    # Calculate progress and draw foreground bar (white, with rounded corners)
    progress_width = int((progress / total_days) * (bar_x2 - bar_x1))
    progress_bar_x2 = bar_x1 + progress_width
    draw.rounded_rectangle([bar_x1, bar_y1, progress_bar_x2, bar_y2], radius=radius, fill="white")

    img.save("youtube_banner.png")

def update_youtube_banner():
    # Load credentials
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(TEMP_SECRET_FILE, SCOPES)
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
