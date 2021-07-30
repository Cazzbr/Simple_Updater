import os
from sys import executable, argv
import shutil
import tempfile
import json
from abc import ABC, abstractmethod
from urllib import request
from .Libs.UpdateInterface import AskToUpdate, UpdateProgress
import zipfile
from time import time, sleep, ctime

class CallBacks():
    def __init__(self, CallBackGauge, CallBackStatus, CallBackCancel) -> None:
        self.CallBackGauge = CallBackGauge
        self.CallBackStatus = CallBackStatus
        self.CallBackCancel = CallBackCancel
    
    def DoCallBackForward(self, status, gauge):
        if self.CallBackStatus != None:
            self.CallBackStatus(status)
        if self.CallBackGauge != None:
            self.CallBackGauge(gauge)
    
    def DoCancel(self):
        self.DoCallBackForward("Exiting...", 100)
        self.CallBackCancel()

    def DoUpdateStatus(self, status):
        if self.CallBackStatus != None:
            self.CallBackStatus(status)

class DoTheUpdate():
    def __init__(self, AppSelf):
        self.cancel = False
        self.GetNewFiles = AppSelf.GetNewFiles
        self.temp_folder = "Simple_Updater " + ctime(time())
        self.AppSelf = AppSelf
    
    def DoUpdate(self, CallBackGauge = None, CallBackStatus = None, CallBackCancel = None):
        call_backs = CallBacks(CallBackGauge, CallBackStatus, CallBackCancel)
        call_backs.DoCallBackForward("Creating a temporary folder...", 1)
        temp_app_folder = os.path.join(tempfile.gettempdir(), self.temp_folder)
        if not os.path.isdir(temp_app_folder):os.mkdir(temp_app_folder)
        if not self.cancel:
            call_backs.DoCallBackForward("Downloading the new version, please wait...", 2)
            get_file = self.GetNewFiles(temp_app_folder)
            if get_file != True:
                call_backs.DoCallBackForward(f"There was an error downloading the file {get_file} - Exiting in 5", 2)
                sleep(5)
                call_backs.DoCancel()
            else:
                call_backs.DoCallBackForward("The required files has been downloaded, Installing...", 50)
            if not self.cancel:
                app_folder = os.getcwd()
                bkp_folder = os.path.join(os.path.dirname(app_folder), os.path.split(app_folder)[1]+ "_BKP")
                if os.path.isdir(bkp_folder):
                    shutil.rmtree(bkp_folder)               
                os.mkdir(bkp_folder)
                file_names = os.listdir(app_folder)
                for f in file_names:
                    shutil.move(os.path.join(app_folder, f), os.path.join(bkp_folder,f))
                if not self.cancel:
                    call_backs.DoCallBackForward("Copying files, Please wait...", 52)
                    new_file_name = os.listdir(temp_app_folder)
                    with zipfile.ZipFile(os.path.join(temp_app_folder, new_file_name[0]), 'r') as zip_ref:
                        zip_ref.extractall(app_folder)
                    if not self.cancel:
                        call_backs.DoCallBackForward("Finished copying files! Removing backup folder", 90)
                        shutil.rmtree(bkp_folder)
                        call_backs.DoCallBackForward("Finished the clean up! Restarting in 2...", 100)
                        sleep(2)
                        self.AppSelf.restart_program()
                    else:
                        call_backs.DoCallBackForward("Reverting changes, please wait...", 52)
                        shutil.rmtree(app_folder)
                        shutil.move(bkp_folder, app_folder)
                        call_backs.DoCancel()
                else:
                    call_backs.DoCallBackForward("Reverting changes, please wait...", 50)
                    shutil.move(bkp_folder, app_folder)
                    call_backs.DoCancel()
            else:
                call_backs.DoCancel()
        else:
            call_backs.DoCancel()

    def CancelUpdate(self):
        self.cancel = True

class SimpleUpdater(ABC):
    ''' Simple Updater main class, recieves a location to a json file and check the app version and compare with a local one. Optionally a relative path can be passed for the local json file. Egg: /includes/ '''

    def __init__(self, file_location: str, json_relative_path: str):
        self.file_location = file_location
        self.current_json_file_path = os.path.join(os.getcwd(), json_relative_path)

    def LocalJson(self):
        with open(self.current_json_file_path) as f:
            Version_Ctrl = json.load(f)
        return Version_Ctrl
    
    @abstractmethod
    def GetJsonFile(self):
        ''' Gets the json object to check the upstream version, if the file is locally configured (internal netwok) '''
    
    @abstractmethod
    def GetNewFiles(self):
        ''' Gets the updated program files from the correct source '''

    def DoWeNeedToUpdate(self):
        ''' Compare the upstream json file with the local file '''
        
        local_json_file = self.LocalJson()
        remote_json = self.GetJsonFile()
        if local_json_file["Version"] == remote_json["Version"]:
            return False
        else:
            return f"Current: {local_json_file['Version']} - New: {remote_json['Version']}"
    
    def Update(self):
        update = self.DoWeNeedToUpdate()
        if update != False:
            update = AskToUpdate("Should update?")
            if update.update:
                update_obj = DoTheUpdate(self)
                UpdateProgress("title", update_obj.DoUpdate, update_obj.CancelUpdate)
        return update
    
    def restart_program(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = executable
        os.execl(python, python, * argv)


class SimpleUpdaterLocal(SimpleUpdater):

    def __init__(self, file_location: str, json_relative_path: str):
        super().__init__(file_location, json_relative_path)

    def GetJsonFile(self):
        ''' Gets the json object to check the upstream version, if the file is locally configured (internal netwok) '''

        with zipfile.ZipFile(self.file_location, 'r') as zip:
            files = zip.namelist()
            for file in files:
                if file.endswith(".json"):
                    jsonfile = file
            read_json = zip.read(jsonfile)
            Version_Ctrl = json.loads(read_json.decode("utf-8"))        
        return Version_Ctrl

    def GetNewFiles(self, dest):
        try:
            shutil.copy(self.file_location, dest)
            return True
        except Exception as error:
            return error

class SimpleUpdaterUrl(SimpleUpdater):
    
    def __init__(self, file_location: str, json_relative_path: str):
        super().__init__(file_location, json_relative_path)
        
    
    def GetJsonFile(self):
        ''' Gets the json object to check the upstream version, if the file is locally configured (internal netwok) '''
        
        return request.urlopen(self.file_location).read()
        #return url_content.read()
    
    def GetNewFiles(self):
        pass

if __name__ == "__main__":
    test = SimpleUpdaterLocal("/home/luciano/SimpleUpdate/Simple_Update.zip", "Version_Ctrl.json")
    #test2 = SimpleUpdaterUrl("https://google.com")
    test.Update()
