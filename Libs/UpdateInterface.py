from os import path
from wx import MessageDialog, App, Frame, Panel, Gauge, Button, StaticText, Image, BITMAP_TYPE_ANY, StaticBitmap, BoxSizer, ID_ANY, VERTICAL, HORIZONTAL, EXPAND, ALL, CENTER, LEFT, RIGHT, BOTTOM, YES_NO, ICON_QUESTION, ID_YES, EVT_BUTTON, CallAfter, ALIGN_CENTER_HORIZONTAL, ALIGN_CENTER_VERTICAL
from .KThread import KThread

class SearchingForUpdatesWarning(Frame):
    def __init__(self, func, app = False, title = "Simple Updater", msg = "Searching for new Updates, please wait..."):
        self.Update = False
        self.search_updates = KThread(target=func, args=(self.close_CallBack,))
        self.search_updates.start()
        self.app = app
        if not self.app:
            self.app = App()
        Frame.__init__(self, None, title=title)
        panel = Panel(self)
        panel_sizer = BoxSizer(VERTICAL)
        text = StaticText(panel, ID_ANY, msg)
        panel_sizer.AddStretchSpacer()
        panel_sizer.Add(text, 1, ALL | ALIGN_CENTER_HORIZONTAL, 20)
        panel_sizer.AddStretchSpacer()
        panel.SetSizer(panel_sizer)
        self.Centre()
        self.Show()
        self.app.MainLoop()

    def close_CallBack(self, update):
        CallAfter(lambda update = update:self.close_window(update))
    
    def close_window(self, update):
        self.search_updates.join()
        self.Close()
        self.Update = update

class AskToUpdate():
    def __init__(self, message: str, title: str = "Simple Updater", app: App = False):
        self.app = app
        if not self.app:
            self.app = App()
        dlg = MessageDialog(None, message, title, YES_NO | ICON_QUESTION)
        result = dlg.ShowModal()
        if result == ID_YES:
            self.update = True
        else:
            self.update = False

class UpdateProgressPanel(Panel):
    def __init__(self, parent, imageFile):
        self.parent = parent
        Panel.__init__(self, parent)
        sizer = BoxSizer(VERTICAL)
        if imageFile != None:
            png = Image(imageFile, BITMAP_TYPE_ANY).ConvertToBitmap()
            image = StaticBitmap(self, ID_ANY, png)
        else:
            png = Image(path.join(path.dirname(__file__), "header.png"), BITMAP_TYPE_ANY).ConvertToBitmap()
            image = StaticBitmap(self, ID_ANY, png)
        self.Progress = Gauge(self, range=100)
        self.UpdateStatus = StaticText(self, ID_ANY, "Status")
        btn = Button(self, ID_ANY, "Cancel")
        btn_sizer = BoxSizer(HORIZONTAL)
        btn_sizer.Add(self.UpdateStatus, 1, LEFT, 10)
        btn_sizer.Add(btn, 0, RIGHT, 10)
        
        sizer.Add(image, 1, CENTER)
        sizer.Add(self.Progress, 0, ALL | EXPAND, 10)
        sizer.Add(btn_sizer, 0, EXPAND | BOTTOM, 10)
        self.SetSizer(sizer)
        
        self.Bind(EVT_BUTTON, self.cancel_clicked, btn)

        self.thread = KThread(target=lambda: self.parent.update_obj(CallBackGauge = self.UpdateGauge,  CallBackStatus = self.UpdateStatusCallBack, CallBackCancel = self.parent.ExitUpdater))
        self.thread.start()   
    
    def cancel_clicked(self, e):
        if self.parent.cancel_obj != None:
            self.UpdateStatus.SetLabel("Trying to cancel the Update")
            e.GetEventObject().Disable()
            self.parent.cancel_obj()
    
    def UpdateGauge(self, status):
        def updateGui():
            self.Progress.SetValue(status)
        CallAfter(updateGui)

    def UpdateStatusCallBack(self, status: str):
        def updateGUI():
            self.UpdateStatus.SetLabel(status)
        CallAfter(updateGUI)

        

class UpdateProgress(Frame):
    def __init__(self, title, update_obj, cancel_obj = None, image: str = None, app: App = False):
        if not app:
            app = App()
        self.update_obj = update_obj
        self.cancel_obj = cancel_obj
        Frame.__init__(self, None, title=title)
        sizer = BoxSizer(VERTICAL)
        self.Progress = UpdateProgressPanel(self, image)
        sizer.Add(self.Progress, 1, EXPAND)
        self.SetSizer(sizer)
        self.Fit()
        self.Show()
        app.MainLoop()
    
    def ExitUpdater(self):
        self.Close()

if __name__ == "__main__":
    SearchingForUpdatesWarning()
