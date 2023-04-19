import os
import tarfile
import dropbox
import re
from tqdm import tqdm
import subprocess

class utils:
    @staticmethod
    def natural_sort(l):
        """ Sort the given iterable in the way that humans expect.""" 
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)
    
    @staticmethod
    def split_tar(folder_path, output_dir, split_size):
        tar_filename = os.path.basename(folder_path) + ".tar.gz"
        tar_file_path = os.path.join(output_dir, tar_filename)
        cmd = f"tar -cvzf - {folder_path} | split -b {split_size} - {tar_file_path}-part"
        subprocess.run(cmd, shell=True, check=True)

def upload_folder_to_dropbox(backup_folder, dropbox_destination_path, access_token_path):
    # Read access token from file
    with open(access_token_path) as f:
        access_token = f.read().strip()

    # Path containing the split tar files
    split_tar_files_path = os.path.join(os.path.dirname(backup_folder), "backup_splits")
    if not os.path.exists(split_tar_files_path):
        os.makedirs(split_tar_files_path)
    # split the tar file into small chunks
    utils.split_tar(backup_folder, split_tar_files_path, "150M")
    
    # Get all split filenames in the folder
    filenames = os.listdir(split_tar_files_path)
    file_list = [os.path.join(split_tar_files_path, f) for f in filenames if os.path.isfile(os.path.join(split_tar_files_path, f))]
    chunk_names = utils.natural_sort(file_list)
    

    print(f'Folder {backup_folder} split into {len(chunk_names)} chunks.')

    # upload the tar file chunks to Dropbox
    dbx = dropbox.Dropbox(access_token)
    try:
        account_info = dbx.users_get_current_account()
        print(f"Your Dropbox account: {account_info.name.display_name} ({account_info.email})")
    except dropbox.exceptions.AuthError as e:
        print(f"Invalid access token: {e}")

    for _, chunk_name in enumerate(tqdm(chunk_names)):
        with open(chunk_name, 'rb') as chunk_file:
            chunk_data = chunk_file.read()

        chunk_upload_session = dbx.files_upload_session_start(chunk_data)
        cursor = dropbox.files.UploadSessionCursor(session_id=chunk_upload_session.session_id, offset=len(chunk_data))
        commit = dropbox.files.CommitInfo(path=f'{dropbox_destination_path}/{os.path.basename(chunk_name)}', mode=dropbox.files.WriteMode('add', None), autorename=True)
        dbx.files_upload_session_finish(chunk_data, cursor, commit)

        # delete the chunk file from local disk
        os.remove(chunk_name)
    
    # remove the split folder
    os.rmdir(split_tar_files_path)
    print(f'Upload of tar file chunks to Dropbox completed.')

    
def download_folder_from_dropbox(dropbox_folder_path, local_destination_path, access_token_path):
    """
    Dowloads a folder (containing multiple tar files) from Dropbox to local disk.

    Args:
        dropbox_folder_path (str): The path to the folder to download in Dropbox (must begin with /).
        local_destination_path (str): The local path to the folder to save the downloaded data.
        access_token_path (str): The path to the file containing the Dropbox access token.

    Returns:
        None
    """
    # Read access token from file
    with open(access_token_path) as f:
        access_token = f.read().strip()
        
    # Check if the local destination path exists and create it if it doesn't
    if not os.path.exists(local_destination_path):
        os.makedirs(local_destination_path)
    
    # Authenticate with Dropbox API
    dbx = dropbox.Dropbox(access_token)
    try :
        account_info = dbx.users_get_current_account()
        print(f"Your Dropbox account: {account_info.name.display_name} ({account_info.email})")
    except dropbox.exceptions.AuthError as e:
        print(f"Invalid access token: {e}")

    # List all the files in the Dropbox folder
    chunk_names = []
    for entry in dbx.files_list_folder(dropbox_folder_path).entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            chunk_names.append(entry.name)
    chunk_names = utils.natural_sort(chunk_names)
    
    # Download the tar file chunks
    for chunk_name in chunk_names:
        local_file_path = os.path.join(local_destination_path, chunk_name)
        with open(local_file_path, "wb") as f:
            metadata, res = dbx.files_download(path=dropbox_folder_path+'/'+chunk_name)
            f.write(res.content)
            print(f"{chunk_name} downloaded to {local_destination_path}")
    
    # # Combine the tar file chunks into a single tar file
    
    
    # # Extract the tar file
    # print(f'Extracting {tar_file_path}...')
    # with tarfile.open(tar_file_path, 'r:gz') as tar:
    #     tar.extractall(local_destination_path)
    # print(f'Tar file {tar_file_path} extracted.')

    # # Delete the tar file
    # os.remove(tar_file_path)
    # print(f'Tar file {tar_file_path} deleted.')

  


def main():
    # ############### To be used for uploading a folder to Dropbox ###############
    # # backup folder
    # backup_folder = '/hdd2/extra_home/hkumar64/random_data'
    # # Dropbox destination path
    # dropbox_destination_path = '/backup_folder_test'
    # # access token file
    # access_token_path = '/hdd2/extra_home/hkumar64/dropbox_backup_util/.dropbox_access_token'
    # upload_folder_to_dropbox(backup_folder, dropbox_destination_path, access_token_path)
    # ############################################################################
    # exit()
    ############### To be used for downloading a folder from Dropbox ###############
    # Dropbox folder path
    dropbox_folder_path = '/backup_folder_test'
    # access token file
    access_token_path = '/hdd2/extra_home/hkumar64/dropbox_backup_util/.dropbox_access_token'
    # local destination path
    local_destination_path = '/hdd2/extra_home/hkumar64/random_data_download'
    download_folder_from_dropbox(dropbox_folder_path, local_destination_path, access_token_path)
    ##################################################################################
if __name__ == '__main__':
    main()