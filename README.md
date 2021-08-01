# Simple_Updater
Simple app updater for local network / web

# To Do
Everything


# Goal
Create a simple python app updater that download all the files from the local server / web and replace everything on the machine

* Initialize the app with only the local netwrok address or web address to check a json file.
* json file contains the app version in a standard way.
* verify if the app need to be updated.
* returns:
* * if the file is not available on the supplied path, return Flase;
* * if the file exists but the versions are the same, return True
* * if the file are different, ask to do it;
* * * if press yes, update the files and restart the app
* * * if press no, return message with the version of the json files
