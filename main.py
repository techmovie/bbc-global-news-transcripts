import feedparser
import whisper_timestamped as whisper
import requests
import os
import pickle
from datetime import datetime
import re


RSS_URL = "https://podcasts.files.bbci.co.uk/p02nq0gn.rss"

SEEN_ENTRIES_FILE = "seen_entries.pkl"

if os.path.exists(SEEN_ENTRIES_FILE):
    with open(SEEN_ENTRIES_FILE, 'rb') as f:
        seen_entries = pickle.load(f)
else: 
  seen_entries = set()
       
def format_timestamp(seconds):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def get_transcript(audio_path):
  try:
    audio = whisper.load_audio(audio_path)
    model = whisper.load_model('base',device="cpu")
    result = whisper.transcribe(model, audio, beam_size=5, best_of=5, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0))
    result_text = ""
    for segment in result["segments"]:
      result_text += f'*{format_timestamp(segment["start"])}- {format_timestamp(segment["end"])}* : {segment["text"]}\n'
    return result_text
  except Exception as e:
    print(e)
 

def fetch_rss_save_ids_only():
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        seen_entries.add(entry.id)

    with open(SEEN_ENTRIES_FILE, 'wb') as f:
        pickle.dump(seen_entries, f)


def fetch_rss_audio():
  try:
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries:
        if entry.id not in seen_entries:
            title = entry.title
            audio_url = entry["ppg_enclosuresecure"]["url"]
            pubdate = entry["published"]
            formatted_date = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
            year,month = formatted_date.split("-")[0],formatted_date.split("-")[1]
            file_name = re.sub('[:\s\'\"()]','_', title)
            print("Downloading:", file_name)
            audio_file = f"{file_name}.mp3"
            with open(audio_file, 'wb') as f:
              file_content = requests.get(audio_url).content
              f.write(file_content)
            transcript = get_transcript(audio_file)
            folder_name = f"transcripts/{year}/{month}"
            if not os.path.exists(folder_name):
              print("Creating folder:", folder_name)
              os.makedirs(folder_name)
            with open(f"{folder_name}/{formatted_date.replace('-','_')}_{file_name}.md", "w") as f:
              f.write(transcript)
            seen_entries.add(entry.id)
            with open(SEEN_ENTRIES_FILE, 'wb') as f:
              pickle.dump(seen_entries, f)
            os.unlink(audio_file)
  except TimeoutError as e:
    print('Failed to connect rss address:', e)
  except IOError as e:
    print('Failed to open file:', e)
  except Exception as e:
    print(e)


if not os.path.exists(SEEN_ENTRIES_FILE):
  fetch_rss_save_ids_only()

fetch_rss_audio()
