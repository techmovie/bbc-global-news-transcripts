# BBC Global News Podcast Transcripts

This project fetches the RSS feed of the BBC Global News podcast, downloads the audio files, transcribes them, and saves the transcripts as text files.

## Requirements

- Python 3.6 or higher
- `feedparser` library
- `whisper-timestamped` library
- `requests` library

## Installation

1. Clone the repository: `git clone https://github.com/techmovie/bbc-global-news-transcripts.git`
2. Install the required libraries: `pip install -r requirements.txt`

## Usage

1. Run the `main.py` file: `python main.py`
2. The script will download any new audio files from the RSS feed, transcribe them, and save the transcripts as text files in the `transcripts` folder.
3. You can also find all the history transcripts in the `transcripts` folder. They were created by the GitHub action automatically.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

