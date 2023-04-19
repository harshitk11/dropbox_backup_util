# Dropbox Backup Script

This script allows you to upload a folder to Dropbox and download it back to your local machine. 

Folders can be arbitrarily large. 
## Getting Started
NOTE: Downloader is buggy right now. Dropbox may be messing with the split tar files. Upon concat post-downloading the combined tar file becomes corrupt.

#### Prerequisites
To use this script, you will need:

- Python 3.6 or higher installed on your machine
- A Dropbox account with access to the Dropbox API
#### Setting up the Dropbox API
Before running the script, you need to set up an access token for the Dropbox API. Here's how:

1. Go to the Dropbox App Console.
2. Choose "Scoped access".
3. Choose the "Full dropbox" scope.
4. Give your app a name <your-app-name>.
5. Click "Create app".
6. Under Permissions -> Files and folders -> Check files.content.write and files.content.read. Submit the changes.
6. Under Settings -> In the "OAuth 2" section, click the "Generate" button next to "Access token".
Copy the generated access token and save it to a file named access_token.txt in the same directory as the script.
Note that you also need to provide write permissions to your Dropbox account in order to upload files.

#### Usage
- Place the files you want to upload to Dropbox in a folder.
- Update the backup_folder and dropbox_destination_path variables in the script to match the folder path and the Dropbox destination folder path, respectively. Dropbox address of the backup_folder will be Apps/<your-app-name>/destination_folder_path. NOTE: destination_folder_path should start with '/'.
- Run the script with python backup_to_dropbox.py.
The script will upload the folder to Dropbox and download it back to your local machine to verify that the upload was successful.
