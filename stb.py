import requests
import threading
import zipfile
import numpy as np
import posixpath
import logging
import time


class SpeechToBlendshape(object):

    def __init__(
        self,
        api_url:str = 'http://10.15.89.69:8001/api/'
    ):
        self._api_url = api_url
        
        self._upload_api = posixpath.join(self._api_url, 'upload_norender')
        self._get_status_api = lambda url: posixpath.join(self._api_url, 'status', url)
        self._get_download_api = lambda url: posixpath.join(self._api_url, 'download', url)
        
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
    
    def api_check_status(self, uid: str) -> bool:
        response = requests.get(self._get_status_api(uid))
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()['done']

    def api_download(self, uid: str, output_path: str) -> None:
        response = requests.get(self._get_download_api(uid)) # GET a ZIP file
        if response.status_code != 200:
            response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
    
    def download_result(self, uid: str, output_path: str) -> None:

        def check_and_download():
            self._logger.debug('Checking status...')
            if self.api_check_status(uid):
                self._logger.info('Downloading...')
                self.api_download(uid, output_path)
            else:
                self._logger.debug('Failed...')
        
        while True:
            check_and_download()
            if self.api_check_status(uid):
                break
            time.sleep(0.3)
            
        self._logger.info('Downloaded.')
    

    def to_blendshape(self, wav_path: str, output_path: str) -> np.ndarray:
        wav_file = open(wav_path, 'rb')
        # npy_file = open(npy_path, 'rb')
        files = {
            'wav': wav_file,
            # 'npy': npy_file
        }
        self._logger.info('Uploading...')
        responese = requests.post(self._upload_api, files=files)
        wav_file.close()
        # npy_file.close()

        if responese.status_code != 200:
            responese.raise_for_status()
        
        # Get uid from response
        uid = responese.json()['uid']

        # Check status of uid every 200ms until it is done
        self._logger.info('Waiting for result...')
        self.download_result(uid, output_path=output_path)
        
        # unzip result
        self._logger.info('Unzipping...')
        with zipfile.ZipFile(output_path, 'r') as zip_ref:
            zip_ref.extractall('result')
        self._logger.info('Done.')


# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     stb = SpeechToBlendshape()
#     stb.to_blendshape(
#         wav_path='test.wav',
#         output_path='result/test.zip'
#     )