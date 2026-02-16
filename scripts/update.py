import json
import os
import subprocess
import time
from datetime import datetime

# Configuration
WORKSPACE = "/Users/maxx/.openclaw/workspace"
PROJECT_DIR = os.path.join(WORKSPACE, "smart-frame")
DATA_FILE = os.path.join(PROJECT_DIR, "data.json")
HTML_FILE = os.path.join(PROJECT_DIR, "index.html")
FTP_HOST = "192.168.100.12"
FTP_PORT = "2221"

def update_data():
    print("Updating data...")
    # Read current data
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    # 1. Update Weather (Mocking skill call behavior here for automation)
    # In a real run, we'd call open-meteo or wttr.in
    try:
        # Simple curl to open-meteo for Alajuela
        res = subprocess.check_output(['curl', '-s', 'https://api.open-meteo.com/v1/forecast?latitude=10.0163&longitude=-84.2116&current_weather=true&hourly=relative_humidity_2m,uv_index'], text=True)
        w_data = json.loads(res)
        data['weather']['temp_c'] = str(round(w_data['current_weather']['temperature']))
        data['weather']['wind_kmh'] = str(round(w_data['current_weather']['windspeed']))
        # We'd map weathercodes to conditions here
    except:
        pass

    # 2. Update Date
    data['maxx_status']['date'] = datetime.now().strftime("%A, %d %b").capitalize()

    # Save data
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data

def update_html_static(data):
    print("Injecting data into HTML for screenshotting...")
    with open(HTML_FILE, 'r') as f:
        content = f.read()

    # Update hardcoded values in HTML to ensure screenshot is never empty
    content = content.replace('id="w-loc">...', f'id="w-loc">{data["weather"]["location"]}')
    content = content.replace('id="w-cond">...', f'id="w-cond">{data["weather"]["condition"]}')
    content = content.replace('id="w-temp">...', f'id="w-temp">{data["weather"]["temp_c"]}°')
    # ... and so on for all IDs. For a robust automation, we use a template engine or regex.
    
    # Simple strategy: Just make sure the HTML file in the repo ALWAYS has the latest state hardcoded 
    # as well as the dynamic script.
    
    with open(HTML_FILE, 'w') as f:
        f.write(content)

def generate_and_upload():
    # Capture current counter
    try:
        res = subprocess.check_output(['lftp', '-c', f'open ftp://{FTP_HOST}:{FTP_PORT}; ls'], text=True)
        existing = [line.split()[-1] for line in res.strip().split('\n') if 'Dashboard_' in line]
        nums = [int(f.split('_')[1].split('.')[0]) for f in existing if '_' in f]
        last_num = max(nums) if nums else 0
    except:
        last_num = 0

    new_num_1 = last_num + 1
    new_num_2 = last_num + 2
    
    file_1 = f"Dashboard_{new_num_1:05d}.png"
    file_2 = f"Dashboard_{new_num_2:05d}.png"
    
    print(f"Generating {file_1} and {file_2}...")
    
    # Take screenshot (This part requires the browser tool via OpenClaw API)
    # For automation, we assume the agent runs this, so we'll just note the command
    
    # Final step: cleanup FTP
    # lftp -c "open ...; rm Dashboard_old..."

if __name__ == "__main__":
    data = update_data()
    # update_html_static(data)
    print("Automation script ready. Pending full browser integration.")
