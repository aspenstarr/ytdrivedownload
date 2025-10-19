import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


import time
import re
import gdown
import os
import json

DOWNLOAD_RECORD_FILE = "downloaded.json"

def load_downloaded_ids():
    if not os.path.exists(DOWNLOAD_RECORD_FILE):
        return set()
    with open(DOWNLOAD_RECORD_FILE, "r") as f:
        return set(json.load(f))

def save_downloaded_ids(ids):
    with open(DOWNLOAD_RECORD_FILE, "w") as f:
        json.dump(sorted(list(ids)), f, indent=2)



# Get video urls


def get_video_urls(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'dump_single_json': True,
        'force_generic_extractor': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        entries = info.get('entries', [])
        for i, entry in enumerate(entries[:600]):
            print(f"{i+1}. {entry.get('title')}")
        video_urls = [entry['url'] for entry in entries if 'url' in entry]

  
    return video_urls


# Get pinned comments

def get_pinned_comment(video_url, headless=False):
   from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def get_pinned_comment(video_url, headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.binary_location = "/opt/google/chrome/google-chrome"

    chromedriver_path = "/home/aspen/Videos/chromedriver-linux64/chromedriver"

    driver = webdriver.Chrome(
        service=Service(chromedriver_path),
        options=chrome_options
    )

    try:
        driver.get(video_url)

        # Wait for the comments section to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "ytd-comments"))
        )
        time.sleep(2)

        # Scroll down to load comments
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        # Find all visible comment threads
        threads = driver.find_elements(By.XPATH, "//ytd-comment-thread-renderer")

        for i, thread in enumerate(threads):
            try:
                # Check if this thread has a pinned badge
                badge = thread.find_element(By.XPATH, ".//ytd-pinned-comment-badge-renderer")
                text = thread.find_element(By.ID, "content-text").text
                print(f"✅ Found pinned comment in thread {i}")
                return text
            except NoSuchElementException:
                continue

        print(" No pinned comment found.")
        return None

    except Exception as e:
        print(f" Error: {e}")
        return None
    finally:
        driver.quit()

# extract Google Drive links


def extract_drive_links(text):
    if not text:
        return []
    drive_link_pattern = r'(https?://(?:drive\.google\.com)/(?:[^\s]+))'
    links = re.findall(drive_link_pattern, text)
    return links


# download from Google Drive

def get_drive_id(url):
    patterns = [
        r'drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com\/open\?id=([a-zA-Z0-9_-]+)',
        r'drive\.google\.com\/drive\/folders\/([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def download_drive_link(url, output_folder="downloads"):
    drive_id = get_drive_id(url)
    if not drive_id:
        print(f"[!] Invalid or unsupported Drive URL: {url}")
        return

    os.makedirs(output_folder, exist_ok=True)

    if "folders" in url:
        print(f"[↓] Downloading folder: {url}")
        gdown.download_folder(url, output=output_folder,
                              quiet=False, use_cookies=False)
    else:
        file_url = f"https://drive.google.com/uc?id={drive_id}"
        print(f"[↓] Downloading file: {file_url}")
        gdown.download(file_url, output=os.path.join(
            output_folder, f"{drive_id}.download"), quiet=False, use_cookies=False)


# main logic

def main(channel_url):
    print(f"Fetching video URLs from channel: {channel_url}")
    video_urls = get_video_urls(channel_url)
    print(f" Found {len(video_urls)} videos.")
    
    
    downloaded_ids = load_downloaded_ids()
    newly_downloaded = set()

    for video_url in video_urls:
        full_url = video_url if video_url.startswith("http") else f"https://www.youtube.com/watch?v={video_url}"

        print(f" Processing video: {full_url}")
        
        video_id = full_url.split("v=")[-1].split("&")[0]
        
        if video_id in downloaded_ids:
            print("⏩ Skipping (already processed).")
            continue

        pinned_comment = get_pinned_comment(full_url)
        if not pinned_comment:
            continue

        drive_links = extract_drive_links(pinned_comment)
        if not drive_links:
            print(" No Google Drive links found in pinned comment.")
            continue

        print(f" Found {len(drive_links)} Google Drive link(s):")
        for link in drive_links:
            print(f" → {link}")
            download_drive_link(link)
            drive_id = get_drive_id(link)
            if drive_id:
                newly_downloaded.add(drive_id)
    
    
    downloaded_ids.update(newly_downloaded)
    save_downloaded_ids(downloaded_ids)




# RUN

if __name__ == "__main__":
    # Replace with actual channel URL ("/videos" optional)
    CHANNEL_URL = "https://www.youtube.com/@vazin./videos"
    main(CHANNEL_URL)
