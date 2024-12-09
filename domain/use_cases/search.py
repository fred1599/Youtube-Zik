from adapters.pytube_adapter import PyTubeAdapter

class SearchUseCase:
    def __init__(self, pytube_adapter: PyTubeAdapter):
        self.pytube_adapter = pytube_adapter

    def search(self, query):
        return self.pytube_adapter.search_videos(query)
