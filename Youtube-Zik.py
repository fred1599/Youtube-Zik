# coding: utf8
import wx
import time
from time import gmtime, strftime
import os, sys
from os import listdir
from os.path import *
import wx.lib.agw.hyperlink as hl
import threading
from pytubefix import YouTube, Search
from pytubefix.cli import on_progress
from collections import deque

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, None, id, title, wx.DefaultPosition, wx.Size(515, 815),style=wx.MINIMIZE_BOX|wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX|wx.STAY_ON_TOP)

        #Panel pour affichage
        self.panel = wx.Panel(self,-1)
        self.panel.Fit()
        self.panel.Show()
        #On capture l'event de fermeture de l'app
        self.Bind(wx.EVT_CLOSE,self.on_close,self)

        #Crée la barre d'état (en bas).
        self.CreerBarreEtat()

        #Loader
        self.loader = Loader(self,-1,"Loading...")
        self.loader.Centre()
        
        #Boutons

        #Help 
        self.help = wx.Button(self.panel,-1,"Need help ?")
        self.Bind(wx.EVT_BUTTON, self.show_help, self.help)
        self.help.SetForegroundColour("forest Green")
        self.help.SetFont(wx.Font(12, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False, "Impact" ))
        self.help.SetToolTip(wx.ToolTip('Click if you need help'))

        #widgets vides
        self.txtVideMemo = wx.StaticText(self.panel,-1,"")
        self.txtVideMemo.SetFont(wx.Font(18, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False, "Impact" ))
        self.txtVideMemo.SetForegroundColour(wx.RED)
        
        #widgets
        #Music
        self.txtMus = wx.StaticText(self.panel,-1,"Search on YouTube :")
        self.txtMus.SetFont(wx.Font(11, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False ))

        #Music field
        self.txtBox = wx.TextCtrl(self.panel,-1,size=(300,25),style=wx.TE_PROCESS_ENTER)
        self.txtBox.SetFont(wx.Font(11, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False ))
        self.txtBox.SetHint("Type music/album/artist name here...")
        self.Bind(wx.EVT_TEXT_ENTER,self.get_music,self.txtBox)
        
        #Output
        self.AffichTxt = wx.ListCtrl(self.panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN,size=(440,440))
        self.AffichTxt.InsertColumn(0, "MUSIC TITLES",width=440)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.no_resize, self.AffichTxt)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.download, self.AffichTxt)
        
        #Donate
        self.txt_don = wx.StaticText(self.panel,-1,"Link to Dev's Paypal.me :")

        self.Lien_don = hl.HyperLinkCtrl(self.panel, wx.ID_ANY, 'Thanks if you donate <3',URL="paypal.me/noobpythondev")
        self.Lien_don.SetLinkCursor(wx.CURSOR_HAND)
        self.Lien_don.SetUnderlines(False, False, True)
        self.Lien_don.EnableRollover(True)
        self.Lien_don.SetColours("BLUE", "ORANGE", "BLUE")
        self.Lien_don.SetBold(True)
        self.Lien_don.SetToolTip(wx.ToolTip('Donation link to the no0b Dev ;)'))
        self.Lien_don.UpdateLink()
        
        #Sizer install
        gbox0 = wx.GridBagSizer(10,10)
        gbox0.SetEmptyCellSize((10,10))
        gbox0.Add(self.txt_don,(0,0))
        gbox0.Add(self.Lien_don,(0,1))
        
        #Sizer gestion
        gbox1 = wx.GridBagSizer(10,10)
        gbox1.SetEmptyCellSize((2,2))
        gbox1.Add(self.txtMus,(0,0))
        gbox1.Add(self.txtBox,(0,1))
        gbox1.Add(self.txtVideMemo,(1,1))
        gbox1.Add(self.help,(2,0))

        #Sizer affichage
        gbox2 = wx.GridBagSizer(10,10)
        gbox2.SetEmptyCellSize((10,10))
        gbox2.Add(self.AffichTxt,(0,0))
        
        #DONATE
        box0 = wx.StaticBox(self.panel, -1, "Donation :")
        bsizer0 = wx.StaticBoxSizer(box0, wx.HORIZONTAL)
        sizerH0 = wx.BoxSizer(wx.VERTICAL)
        sizerH0.Add(gbox0, 0, wx.ALL|wx.CENTER, 10)
        bsizer0.Add(sizerH0, 1, wx.EXPAND, 0)
        
        #Zik-DDL
        box1 = wx.StaticBox(self.panel, -1, "Youtube-Zik Downloader :")
        bsizer1 = wx.StaticBoxSizer(box1, wx.HORIZONTAL)
        sizerH1 = wx.BoxSizer(wx.VERTICAL)
        sizerH1.Add(gbox1, 0, wx.ALL|wx.CENTER, 10)
        bsizer1.Add(sizerH1, 1, wx.EXPAND, 0)

        #Affichage
        box2 = wx.StaticBox(self.panel, -1, "Results of YT music search :")
        bsizer2 = wx.StaticBoxSizer(box2, wx.HORIZONTAL)
        sizerH2 = wx.BoxSizer(wx.VERTICAL)
        sizerH2.Add(gbox2, 0, wx.ALL|wx.CENTER, 10)
        bsizer2.Add(sizerH2, 1, wx.EXPAND, 0)

        #--------Ajustement du sizer----------
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(bsizer1, 0,wx.ALL|wx.EXPAND, 10)
        mainSizer.Add(bsizer2, 0,wx.ALL|wx.EXPAND, 10)
        mainSizer.Add(bsizer0, 0,wx.ALL|wx.EXPAND, 10)
        self.panel.SetSizerAndFit(mainSizer)

        #Create dir for DL if not exixts
        if not os.path.exists('Collection'):
            os.makedirs('Collection')

    #Threads wrapper usage : mark @threaded over differents threads
    def threaded(fn):
        def wrapper(*args, **kwargs):
            threading.Thread(target=fn, args=args, kwargs=kwargs).start()
        return wrapper

    #Prevents user from resizing columns width
    def no_resize(self,evt):
        evt.Veto()

    @threaded
    def get_music(self,evt):
        global liste_urls,lst_ziks,title
        liste_ziks=[f for f in listdir("Collection") if isfile(join("Collection", f))]
        lst_ziks = [os.path.splitext(x)[0] for x in liste_ziks]
        liste_urls=deque()
        if (self.AffichTxt.IsEmpty()==False):
            self.AffichTxt.DeleteAllItems()
        zik = self.txtBox.GetValue()
        if (zik!=""):
            self.show_loader()
            self.txtVideMemo.SetLabel("")
            s = Search(zik)
            liste_zik = s.videos
            for i in liste_zik:
                title = i.title
                url = i.watch_url
                liste_urls.appendleft(url)
                self.AffichTxt.InsertItem(0,title)
                self.color_ziks()
                self.check_zik()
                
        else:
            self.txtVideMemo.SetLabel("Enter music name !")
        evt.Skip()        

    def check_zik(self):
        for j in lst_ziks:
            if (j==title):
                index=self.AffichTxt.FindItem(-1,j)
                self.AffichTxt.SetItemTextColour(index,wx.RED)
        
    def download(self,evt):
        i_text = evt.GetText()
        index=self.AffichTxt.FindItem(-1,i_text)
        test_color = self.AffichTxt.GetItemTextColour(index)
        if test_color==wx.RED:
            Connexion = wx.MessageDialog(self, "You already onw this music !"+"\n"+"You cannot download it twice !","Warning window",\
            style=wx.ICON_QUESTION|wx.CENTRE|wx.OK,pos=wx.DefaultPosition) #Definit les attributs de la fenetre de message.
            rep = Connexion.ShowModal() #Affiche le message a l'ecran.
        else:
            url=liste_urls[index]
            yt = YouTube(url)
            stream = yt.streams.get_audio_only()
            stream.download("Collection",mp3=True) # pass the parameter mp3=True to save in .mp3
            self.AffichTxt.SetItemTextColour(index,wx.RED)
        evt.Skip()
        
    def color_ziks(self):
        self.AffichTxt.SetTextColour(wx.BLUE)
        self.hide_loader()
        
    def show_help(self,evt):
        Connexion = wx.MessageDialog(self, "YouTube Downloader Python V1.0 Notice :"+"\n\n"+"Right click on a BLUE coloured music to download it."+"\n"+"To know when download finished just wait until music title turns RED !"+"\n"+"If the music is coloured in RED you already have it in the 'Collection' folder !"+"\n\n"+"That's all folks !","Help window",\
        style=wx.ICON_WARNING|wx.CENTRE|wx.OK,pos=wx.DefaultPosition) #Definit les attributs de la fenetre de message.
        rep = Connexion.ShowModal() #Affiche le message a l'ecran.
        evt.Skip()
        
    @threaded
    def show_loader(self):
        self.loader.Show()

    @threaded
    def hide_loader(self):
        self.loader.Hide()
    
    def Chrono(self):#Chronometre (date )
        stemps = time.strftime("%A %d/%m/%Y") #Definit le format voulu
        self.SetStatusText(stemps,1) #Affiche a droite.
        self.SetStatusText("Developed by François Garbez",0)
    
    def CreerBarreEtat(self):#Creation de la barre d'etat du bas avec l'affichage de la date
        self.CreateStatusBar(2) #Cree une barre de statut (en bas) de deux parties.
        self.SetStatusWidths([-1,150]) #Definit la taille.
        self.Chrono()#Affiche.

    def on_close(self,evt):#On detruit tout :)
        try:
            self.loader.Destroy()
        except:
            pass
        finally:
            self.Destroy()

class Loader(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, None, id, title, wx.DefaultPosition, wx.Size(300, 200),style=wx.MINIMIZE_BOX|wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX|wx.STAY_ON_TOP)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self,-1)
        self.panel.Fit()
        self.panel.Show()

        self.txt = wx.StaticText(self.panel,-1,"Searching Music/Album/Artist Please Wait...")
        self.spinner = wx.ActivityIndicator(self.panel, size=(35, 35))

        sizer.AddStretchSpacer(1)
        sizer.Add(self.txt, 0, wx.ALIGN_CENTER)
        sizer.Add(self.spinner, 1, wx.ALIGN_CENTER)
        sizer.AddStretchSpacer(1)

        self.panel.SetSizerAndFit(sizer)
        self.spinner.Start()

        #usage : put in wx.Frame class, then call Show/Hide or Destroy
        
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "YoutubeZik DDL V1.0")
        frame.Show(True)
        frame.Centre()
        return True
 
if __name__=='__main__':    
 
    app = MyApp()
    app.MainLoop()


### YoutubeZik DDL V1.0 by François GARBEZ 27/07/2024 Tested on python 3.12 Win11 ###
