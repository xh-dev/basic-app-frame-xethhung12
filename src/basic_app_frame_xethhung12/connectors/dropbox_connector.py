import dropbox
import base64
class DropboxConnector():
    def __init__(self, token: str):
        self.dropbox = dropbox.Dropbox(token)
    
    def list_entries(self, path_to_list:str=''):
        for i in self.dropbox.files_list_folder(path_to_list).entries:
            yield i
    
    def get_image_as_base64(self, path_to_download)->str:
        meta, resp = self.dropbox.files_download(path_to_download)
        return base64.b64encode(resp.content).decode('utf-8')
    
    def move(self, fromFile: str, toFile: str):
        return self.dropbox.files_move_v2(fromFile, toFile)
    
    def upload(self, path: str, text: str):
        return self.dropbox.files_upload(text.encode('utf-8'), path, mode=dropbox.files.WriteMode('overwrite'))