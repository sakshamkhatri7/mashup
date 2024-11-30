from yt_dlp import YoutubeDL
import os
import logging
from pydub import AudioSegment

class Download:
    def __init__(self, singer, number, duration):
        self.singer = singer
        self.number = number
        self.duration = duration  # Duration for each song in seconds
        self.SAVE_PATH = f'static/{self.singer}/'
        logging.info(f"Starting download for {self.singer}, {self.number} songs, {self.duration} seconds each.")
        self.download_videos()

    def download_videos(self):
        os.makedirs(self.SAVE_PATH, exist_ok=True)

        search_query = f"ytsearch:{self.singer} music videos"
        downloaded_videos = []
        valid_videos = 0

        def filter_videos(info, *, incomplete):
            if info.get('duration') and info['duration'] > 300:  # 300 seconds = 5 minutes
                logging.info(f"Skipping video: {info['title']} (Duration: {info['duration']} seconds)")
                return 'Video is longer than 5 minutes'
            return None  # Proceed to download if duration <= 5 minutes

        options = {
            'format': 'worstvideo+bestaudio/best',
            'outtmpl': f'{self.SAVE_PATH}%(title)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'noplaylist': True,
            'logger': logging.getLogger(),
            'match_filter': filter_videos,  # Apply filter for skipping long videos
        }

        try:
            while valid_videos < self.number:

                search_query = f"ytsearch{self.number + len(downloaded_videos)}:{self.singer} music videos"
                with YoutubeDL(options) as ydl:
                    result = ydl.extract_info(search_query, download=False)
                    for entry in result['entries']:
                        if entry['id'] not in downloaded_videos:
                            downloaded_videos.append(entry['id'])
                            ydl.download([f'https://www.youtube.com/watch?v={entry["id"]}'])
                            valid_videos += 1
                            if valid_videos >= self.number:
                                break
                logging.info(f"Valid videos downloaded: {valid_videos}/{self.number}")

        except Exception as e:
            logging.error(f"Error during downloading: {e}")
            return

        self.create_mashup()

    def create_mashup(self):
        pathhh = self.SAVE_PATH
        audio_files = [f for f in os.listdir(pathhh) if f.endswith('.mp3')]

        if len(audio_files) < self.number:
            logging.error("Not enough audio files to create a mashup.")
            return

        try:
            # Initialize an empty audio segment for the mashup
            combined = AudioSegment.empty()

            for file in audio_files:
                audio_path = os.path.join(pathhh, file)
                audio = AudioSegment.from_mp3(audio_path)

                # Trim each audio to the specified duration
                trimmed_audio = audio[:self.duration * 1000]  # Convert duration to milliseconds
                combined += trimmed_audio  # Concatenate the trimmed audio

            # Apply fade in and fade out effects
            combined = combined.fade_in(2000).fade_out(3000)

            # Export the final mashup
            combined.export(os.path.join(pathhh, 'mashup.mp3'), format='mp3')

            logging.info("Audio mashup created successfully!")

        except Exception as e:
            logging.error(f"Error during mashup creation: {e}")

