import wx

from domain.use_cases.search import SearchUseCase
from domain.use_cases.download import DownloadUseCase
from adapters.pytube_adapter import PyTubeAdapter
from interface.ui.wxpython.frame import MainFrame

if __name__ == "__main__":
    pytube_adapter = PyTubeAdapter()

    search_use_case = SearchUseCase(pytube_adapter)
    download_use_case = DownloadUseCase(pytube_adapter)

    app = wx.App(False)
    frame = MainFrame(search_use_case, download_use_case)
    frame.Show()
    app.MainLoop()
