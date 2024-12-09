from adapters.pytube_adapter import PyTubeAdapter

class DownloadUseCase:
    def __init__(self, pytube_adapter: PyTubeAdapter):
        self.pytube_adapter = pytube_adapter

    def download(self, url, title):
        self.pytube_adapter.download_video(url, title)
