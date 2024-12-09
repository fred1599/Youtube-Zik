from pytubefix import YouTube, Search

class PyTubeAdapter:
    def download_video(self, url, title):
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path="Video Collection", filename=f"{title}.mp4")

    def search_videos(self, query):
        search = Search(query)
        results = [
            {"title": video.title, "url": video.watch_url}
            for video in search.videos
        ]
        return results
