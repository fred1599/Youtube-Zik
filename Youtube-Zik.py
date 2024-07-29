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

        #RadioButtons
        self.mp3_b = wx.RadioButton(self.panel,-1, label="Format: mp3 (audio only)", style=wx.RB_GROUP)
        self.Bind(wx.EVT_RADIOBUTTON,self.def_mp3,self.mp3_b)
        self.mp4_b = wx.RadioButton(self.panel,-1, label="Format: mp4 (video)")
        self.Bind(wx.EVT_RADIOBUTTON,self.def_mp4,self.mp4_b)
        
        #Boutons
        #Help 
        self.help = wx.Button(self.panel,-1,"Need help ?")
        self.Bind(wx.EVT_BUTTON, self.show_help, self.help)
        self.help.SetForegroundColour("forest Green")
        self.help.SetFont(wx.Font(12, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False, "Impact" ))
        self.help.SetToolTip(wx.ToolTip('Click if you need help'))

        #More Results
        self.more = wx.Button(self.panel,-1,"Need more ?")
        self.Bind(wx.EVT_BUTTON, self.show_more, self.more)
        self.more.SetForegroundColour("Blue")
        self.more.SetFont(wx.Font(12, wx.DEFAULT , wx.NORMAL, wx.NORMAL,False, "Impact" ))
        self.more.SetToolTip(wx.ToolTip('Click to fetch more results'))

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
        self.AffichTxt = wx.ListCtrl(self.panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN,size=(440,400))
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
        gbox1.Add(self.more,(2,1))

        #Sizer affichage
        gbox2 = wx.GridBagSizer(10,10)
        gbox2.SetEmptyCellSize((10,10))
        gbox2.Add(self.mp3_b,(0,0))
        gbox2.Add(self.mp4_b,(1,0))
        gbox2.Add(self.AffichTxt,(2,0))
        
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

        #Create dir for mp3 DL if not exixts
        if not os.path.exists('Audio Collection'):
            os.makedirs('Audio Collection')

        #Create dir for mp4 DL if not exixts
        if not os.path.exists('Video Collection'):
            os.makedirs('Video Collection')

        #Initialize self.test_mp3 var
        self.test_mp3 = self.mp3_b.GetValue()

        self.vmk=0
        self.zmk=0

    #Threads wrapper usage : mark @threaded over differents threads
    def threaded(fn):
        def wrapper(*args, **kwargs):
            threading.Thread(target=fn, args=args, kwargs=kwargs).start()
        return wrapper

    def def_mp3(self,evt):
        self.test_mp3 = self.mp3_b.GetValue()
        evt.Skip()

    def def_mp4(self,evt):
        self.mp3_b.SetValue(False)
        self.test_mp3 = self.mp3_b.GetValue()
        evt.Skip()

    @threaded
    def show_more(self,evt):
        if (self.AffichTxt.IsEmpty()==False):
            s.get_next_results()
            self.fetch_q()
        else:
            self.txtVideMemo.SetLabel("Search for music first !")
        evt.Skip()
    
    #Prevents user from resizing columns width
    def no_resize(self,evt):
        evt.Veto()

    @threaded
    def get_music(self,evt):
        global s,lst_ziks,lst_vids
        liste_ziks=[f for f in listdir("Audio Collection") if isfile(join("Audio Collection", f))]
        liste_vids=[f for f in listdir("Video Collection") if isfile(join("Video Collection", f))]
        lst_ziks = [os.path.splitext(x)[0] for x in liste_ziks]
        lst_vids = [os.path.splitext(x)[0] for x in liste_vids]
        if (self.AffichTxt.IsEmpty()==False):
            self.AffichTxt.DeleteAllItems()
        zik = self.txtBox.GetValue()
        if (zik!=""):
            self.txtVideMemo.SetLabel("")
            s = Search(zik)
            self.fetch_q()
        else:
            self.txtVideMemo.SetLabel("Enter music name !")
        evt.Skip()  

    @threaded
    def fetch_q(self):
        global liste_urls,title
        liste_urls=deque()
        liste_all = s.videos
        for i in liste_all:
            title = i.title
            url = i.watch_url
            liste_urls.appendleft(url)
            self.AffichTxt.InsertItem(0,title)
            self.color_txt()
            self.check_zik()
            self.check_vid()

    def color_txt(self):
        self.AffichTxt.SetTextColour(wx.BLUE)
        
    def check_zik(self):
        if title in lst_ziks:
            for j in lst_ziks:
                if (j==title):
                    self.AffichTxt.SetItemTextColour(0,"PURPLE")
                    self.zmk=1
                if (j==title and self.vmk==1):
                    self.AffichTxt.SetItemTextColour(0,wx.RED)
        else:
            self.zmk=0
                             
    def check_vid(self):
        if title in lst_vids:
            for k in lst_vids:
                if (k==title):
                    self.AffichTxt.SetItemTextColour(0,"FOREST GREEN")
                    self.vmk=1
                if (k==title and self.zmk==1):
                    self.AffichTxt.SetItemTextColour(0,wx.RED)
        else:
            self.vmk=0
                
    def download(self,evt):
        global yt,index
        i_text = evt.GetText()
        index=self.AffichTxt.FindItem(-1,i_text)
        url=liste_urls[index]
        yt = YouTube(url)
        test_color = self.AffichTxt.GetItemTextColour(index)
        if test_color=="PURPLE":
            Connexion = wx.MessageDialog(self, "You already own this Music !"+"\n"+"Do you want to download the video file(mp4) ?","Warning window",\
            style=wx.ICON_QUESTION|wx.CENTRE|wx.YES_NO|wx.CANCEL,pos=wx.DefaultPosition) #Definit les attributs de la fenetre de message.
            rep = Connexion.ShowModal() #Affiche le message a l'ecran.
            if rep == wx.ID_YES:
                    self.dl_vid()
            else:
                pass
        elif test_color=="FOREST GREEN":
            Connexion = wx.MessageDialog(self, "You already own this Video !"+"\n"+"Do you want to download the audio file(mp3) ?","Warning window",\
            style=wx.ICON_QUESTION|wx.CENTRE|wx.YES_NO|wx.CANCEL,pos=wx.DefaultPosition) #Definit les attributs de la fenetre de message.
            rep = Connexion.ShowModal() #Affiche le message a l'ecran.
            if rep == wx.ID_YES:
                self.dl_zik()
            else:
                pass
        elif test_color==wx.RED:
            Connexion = wx.MessageDialog(self, "You already own this Audio and Video !"+"\n"+"You can't download it anymore !","Warning window",\
            style=wx.ICON_QUESTION|wx.CENTRE|wx.OK,pos=wx.DefaultPosition) #Definit les attributs de la fenetre de message.
            rep = Connexion.ShowModal() #Affiche le message a l'ecran.
        else:
            if (self.test_mp3==True):
                self.dl_zik()
            else:
                self.dl_vid()
        evt.Skip()

    @threaded
    def dl_vid(self):
        self.loader.Show()
        stream = yt.streams.get_highest_resolution()
        stream.download("Video Collection")
        self.vmk=1
        if(self.zmk==0):
            self.AffichTxt.SetItemTextColour(index,"FOREST GREEN")
        else:
            self.AffichTxt.SetItemTextColour(index,wx.RED)
        self.loader.Hide()
        
    @threaded
    def dl_zik(self):
        self.loader.Show()
        stream = yt.streams.get_audio_only()
        stream.download("Audio Collection",mp3=True) # pass the parameter mp3=True to save in .mp3
        self.zmk=1
        if (self.vmk==0):
            self.AffichTxt.SetItemTextColour(index,"PURPLE")
        else:
            self.AffichTxt.SetItemTextColour(index,wx.RED)
        self.loader.Hide()
        
    def show_help(self,evt):
        Connexion = wx.MessageDialog(self, "YouTube Downloader Python V2.0 Notice :"+"\n\n"+"Right click on a BLUE coloured music to download it."+"\n"+"To know when download finished just wait until music title color change !"+"\n"+"If the music is coloured in RED you already have it in the 'Collection''s folder !"+"\n\n"+"Press the 'NEED MORE ?' button to fetch more results !"+"\n\n"+"That's all folks !","Help window",\
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

        self.txt = wx.StaticText(self.panel,-1,"Downloading Please Wait...")
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
        frame = MyFrame(None, -1, "YoutubeZik DDL V2.0")
        frame.Show(True)
        frame.Centre()
        return True
 
if __name__=='__main__':    
 
    app = MyApp()
    app.MainLoop()


### YoutubeZik DDL V1.0 by François GARBEZ 27/07/2024 Tested on python 3.12 Win11 ###
