import os

from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio

class FFmpegAdapter:
    def merge_video_audio(self, video_file, audio_file, output_file):
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file not found: {video_file}")
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        try:
            ffmpeg_merge_video_audio(video_file, audio_file, output_file)
            return True
        except Exception as e:
            print(f"Error merging video and audio: {e}")
            return False
