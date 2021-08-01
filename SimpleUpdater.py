import os
from sys import executable, argv
import shutil
import tempfile
import json
from abc import ABC, abstractmethod
from urllib import request
import zipfile
from time import time, sleep, ctime
import __main__ as main
try:
    from .Libs.UpdateInterface import AskToUpdate, UpdateProgress
except Exception:
    from Libs.UpdateInterface import AskToUpdate, UpdateProgress

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
    
    def Stage1_download(self, temp_app_folder):
        self.call_backs.DoCallBackForward("Downloading the new version, please wait...", 2)
        get_file = self.GetNewFiles(temp_app_folder)
        if get_file != True:
            self.call_backs.DoCallBackForward(f"There was an error downloading the file {get_file} - Exiting in 5", 2)
            sleep(5)
            self.call_backs.DoCancel()
            self.CancelUpdate()
        else:
            self.call_backs.DoCallBackForward("The required files has been downloaded, Installing...", 50)

    def Stage2_bkpFiles(self, app_folder, bkp_folder):
        if os.path.isdir(bkp_folder):
            shutil.rmtree(bkp_folder)               
        os.mkdir(bkp_folder)
        file_names = os.listdir(app_folder)
        for f in file_names:
            shutil.move(os.path.join(app_folder, f), os.path.join(bkp_folder,f))
    
    def revert_stage2(self, app_folder, bkp_folder):
        self.call_backs.DoCallBackForward("Reverting changes, please wait...", 50)
        shutil.move(bkp_folder, app_folder)
        self.call_backs.DoCancel()

    def Stage3_moveFiles(self, temp_app_folder, app_folder):
        self.call_backs.DoCallBackForward("Copying files, Please wait...", 52)
        new_file_name = os.listdir(temp_app_folder)
        exec_file_name = os.path.split(main.__file__)[1]
        with zipfile.ZipFile(os.path.join(temp_app_folder, new_file_name[0]), 'r') as zip:
            to_remove = False
            for file in zip.namelist():
                if (os.path.split(file)[1])  == exec_file_name:
                    to_remove = len(os.path.split(file)[0])
            if to_remove:
                for zip_info in zip.infolist():
                    if zip_info.filename[-1] == '/':
                        continue
                    zip_info.filename = zip_info.filename[to_remove:]
                    zip.extract(zip_info, app_folder)

    def revert_stage3(self, app_folder, bkp_folder):
        self.call_backs.DoCallBackForward("There was an error starting the APP! Reverting the changes, please wait...", 52)
        shutil.rmtree(app_folder)
        shutil.move(bkp_folder, app_folder)
        self.call_backs.DoCancel()

    def Stage4_restartAndCheckUpate(self, app_folder, bkp_folder):
        updated = self.AppSelf.DoWeNeedToUpdate()
        if os.path.isfile(main.__file__) and updated:
            self.Stage5_cleanUp(bkp_folder)
            self.AppSelf.restart_program()
        else:
            self.revert_stage3(app_folder, bkp_folder)

    def Stage5_cleanUp(self, bkp_folder):
        shutil.rmtree(bkp_folder)

    def DoUpdate(self, CallBackGauge = None, CallBackStatus = None, CallBackCancel = None):
        self.call_backs = CallBacks(CallBackGauge, CallBackStatus, CallBackCancel)
        self.call_backs.DoCallBackForward("Creating a temporary folder...", 1)
        temp_app_folder = os.path.join(tempfile.gettempdir(), self.temp_folder)
        if not os.path.isdir(temp_app_folder):os.mkdir(temp_app_folder)
        if not self.cancel:
            self.Stage1_download(temp_app_folder)
            if not self.cancel:
                app_folder = os.getcwd()
                bkp_folder = os.path.join(os.path.dirname(app_folder), os.path.split(app_folder)[1]+ "_BKP")
                self.Stage2_bkpFiles(app_folder, bkp_folder)
                if not self.cancel:
                    self.Stage3_moveFiles(temp_app_folder, app_folder)
                    if not self.cancel:
                        self.Stage4_restartAndCheckUpate(app_folder, bkp_folder)
                    else:
                        self.revert_stage3(app_folder, bkp_folder)
                else:
                    self.revert_stage2(app_folder, bkp_folder)
            else:
                self.call_backs.DoCancel()
        else:
            self.call_backs.DoCancel()

    def CancelUpdate(self):
        self.cancel = True

class SimpleUpdater(ABC):
    ''' Simple Updater main class, recieves a location to a json file and check the app version and compare with a local one. Optionally a relative path can be passed for the local json file. Egg: /includes/ '''

    def __init__(self, file_location: str, json_relative_path: str, app_image: str = None):
        self.file_location = file_location
        self.current_json_file_path = os.path.join(os.getcwd(), json_relative_path)
        self.app_image = app_image

    def LocalJson(self):
        if os.path.isfile(self.current_json_file_path):
            with open(self.current_json_file_path) as f:
                Version_Ctrl = json.load(f)
            return Version_Ctrl
        else: return False
    
    @abstractmethod
    def GetJsonFile(self):
        ''' Gets the json object to check the upstream version, if the file is locally configured (internal netwok) '''
    
    @abstractmethod
    def GetNewFiles(self):
        ''' Gets the updated program files from the correct source '''

    def DoWeNeedToUpdate(self):
        ''' Compare the upstream json file with the local file '''

        local_json_file = self.LocalJson()
        self.remote_json = self.GetJsonFile()
        if self.remote_json and local_json_file:
            try:
                if local_json_file["Version"] == self.remote_json["Version"]:
                    return True
                else:
                    return (local_json_file['Version'], self.remote_json['Version'])
            except:
                return False
        else:
            return False
    
    def Update(self):
        update = self.DoWeNeedToUpdate()
        if update != False and update!= True:
            if update[0] < update[1]:
                try:
                    question_text = self.remote_json["question_text"]
                except:
                    question_text = "The application has an update! Do you want to update now?"
                try:
                    question_title = self.remote_json["question_title"]
                except:
                    question_title = "Simple Updater"
                update_Question = AskToUpdate(question_text, question_title)
                if update_Question.update:
                    update_obj = DoTheUpdate(self)
                    UpdateProgress(question_title, update_obj.DoUpdate, update_obj.CancelUpdate, self.app_image)
        return update
    
    def restart_program(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = executable
        os.execl(python, python, * argv)


class SimpleUpdaterLocal(SimpleUpdater):

    def __init__(self, file_location: str, json_relative_path: str, app_image: str = None):
        super().__init__(file_location, json_relative_path, app_image)

    def GetJsonFile(self):
        ''' Gets the json object to check the upstream version, if the file is locally configured (internal netwok) '''

        Version_Ctrl = False
        if os.path.isfile(self.file_location):
            with zipfile.ZipFile(self.file_location, 'r') as zip:
                files = zip.namelist()
                for file in files:
                    if file.endswith(".json"):
                        Version_Ctrl = file
                if Version_Ctrl:
                    read_json = zip.read(Version_Ctrl)
                    Version_Ctrl = json.loads(read_json.decode("utf-8"))        
        return Version_Ctrl

    def GetNewFiles(self, dest):
        try:
            shutil.copy(self.file_location, dest)
            return True
        except Exception as error:
            return error

class SimpleUpdaterUrl(SimpleUpdater):
    
    def __init__(self, file_location: str, json_relative_path: str, json_file_location: str, app_image: str = None):
        self.json_file_location = json_file_location
        super().__init__(file_location, json_relative_path, app_image)
        
    
    def GetJsonFile(self):
        ''' Gets the json object to check the upstream version, if the file is locally configured (internal netwok) '''
        
        file = request.urlopen(self.json_file_location).read()
        Version_Ctrl = json.loads(file)
        return Version_Ctrl
    
    def GetNewFiles(self, dest):
        abs_dest_file_name = os.path.join(dest, os.path.split(self.file_location)[1])      
        try:
            request.urlretrieve(self.file_location, abs_dest_file_name)
            if not os.path.isfile(abs_dest_file_name):
                return 'remote file does not exist'
            return True
        except IOError:
            return 'Error downloading file'

if __name__ == "__main__":
    pass
