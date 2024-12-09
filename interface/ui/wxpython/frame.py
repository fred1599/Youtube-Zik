import wx

from interface.ui.wxpython.custom_message_dialog import CustomMessageDialog
from interface.ui.wxpython.loader import Loader

class MainFrame(wx.Frame):
    def __init__(self, search_use_case, download_use_case):
        super().__init__(None, title="YouTube Downloader", size=(800, 600))
        self.search_use_case = search_use_case
        self.download_use_case = download_use_case
        self.loader = None
        self.setup_ui()

    def setup_ui(self):
        panel = wx.Panel(self)

        self.search_input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search_input.Bind(wx.EVT_TEXT_ENTER, self.on_search)

        search_button = wx.Button(panel, label="Rechercher")
        search_button.Bind(wx.EVT_BUTTON, self.on_search)

        self.result_list = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.result_list.InsertColumn(0, "Titre", width=300)
        self.result_list.InsertColumn(1, "URL", width=400)

        download_button = wx.Button(panel, label="Télécharger")
        download_button.Bind(wx.EVT_BUTTON, self.on_download)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search_input, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(search_button, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.result_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(download_button, flag=wx.EXPAND | wx.ALL, border=5)
        panel.SetSizer(sizer)

    def show_loader(self, message="Chargement..."):
        if self.loader is None:
            self.loader = Loader(self, -1, message)
        self.loader.Show()

    def hide_loader(self):
        if self.loader:
            self.loader.Destroy()
            self.loader = None

    def on_search(self, event):
        query = self.search_input.GetValue().strip()
        if not query:
            CustomMessageDialog(self, "Veuillez entrer un terme de recherche.", "Erreur", wx.ICON_ERROR).ShowModal()
            return

        try:
            self.show_loader("Recherche en cours...")
            videos = self.search_use_case.search(query)

            self.result_list.DeleteAllItems()
            for index, video in enumerate(videos):
                self.result_list.InsertItem(index, video["title"])
                self.result_list.SetItem(index, 1, video["url"])
        except Exception as e:
            CustomMessageDialog(self, f"Erreur lors de la recherche : {str(e)}", "Erreur", wx.ICON_ERROR).ShowModal()
        finally:
            self.hide_loader()

    def on_download(self, event):
        selected_index = self.result_list.GetFirstSelected()
        if selected_index == -1:
            CustomMessageDialog(self, "Veuillez sélectionner une vidéo à télécharger.", "Erreur", wx.ICON_ERROR).ShowModal()
            return

        title = self.result_list.GetItemText(selected_index)
        url = self.result_list.GetItem(selected_index, 1).GetText()

        try:
            self.show_loader(f"Téléchargement de {title} en cours...")
            self.download_use_case.download(url, title)
            CustomMessageDialog(self, f"Téléchargement terminé : {title}", "Succès", wx.ICON_INFORMATION).ShowModal()
        except Exception as e:
            CustomMessageDialog(self, f"Erreur lors du téléchargement : {str(e)}", "Erreur", wx.ICON_ERROR).ShowModal()
        finally:
            self.hide_loader()
