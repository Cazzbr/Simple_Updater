# Simple_Updater
Simple app updater for local network / web

# Goal
Create a simple python app updater that download all the files from the local server / web and replace everything on the machine

* Initialize the app with only a few argument;
* json file contains the app version in a standard way;
* verify if the app need to be updated.
* returns:
* * if the file is not available on the supplied path, or any error happened on the process   --->  return False;
* * if the file exists and everything is fine, but the versions are the same   ---> return True
* * if the file are different and the version upstream is greater than the local version, ask to do it;
* * * if press yes, update the files and restart the app
* * * if press no, return message with the version of the json files;

# Usage

There are 2 main methods on the app:
 - SimpleUpdaterUrl(file_location: str, json_relative_path: str, json_file_location: str, app_image: str = None)
    -- file_location: is the location (on the web) of a .zip file with your full app;
    -- json_relative_path: is the relative path (ex: "libs/versioning.json")
    -- json_file_location: For the web version we need acess to the json file outside the zip file, so we dont need to download all the zip file to check updates;
    -- app_image: relative path for an image you want to use on the updater. This is optional, an default image is inclided;

 - SimpleUpdaterLocal(file_location: str, json_relative_path: str, app_image: str = None)
    -- file_location: is the location (local network) of a .zip file with your full app;
    -- json_relative_path: is the relative path (ex: "libs/versioning.json")
    -- app_image: relative path for an image you want to use on the updater. This is optional, an default image is inclided;

The .json file only need one variable: "Version": ..... (with capital "V")
besides that you can place any info you need on your app (settings or whatever)
there are more 2 optional variables on the json file:
    - "question_title": "This is your custon title for the updater window, and the updated always gets this info for the upstream .json file"
    - "question_text": "This is your custon text for the question for the user if the app should be updated or not, and the updated always gets this info for the upstream .json file"

those two parameters does not block the update, there are default values for them.

## Example of usage for the web version:
    updater = SimpleUpdaterUrl("https://github.com/{YOURUSERNAME}/{YOURAPPNAME}/archive/refs/heads/{BRANCHNAME}.zip", "Includes/Version_Ctrl.json", "https://raw.githubusercontent.com/{YOURUSERNAME}/{YOURAPPNAME}/main/Version_Ctrl.json")
    
    updater.Update()

So, first we create the constructor and then we call the Update() function.