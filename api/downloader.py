import requests
from django.conf import settings
import os.path
from os import path

weight_file_id = '1jbSdlKmAJAgiie_kDFx2Nvs7UPD7DVVr'
weight_destination = '45.pt'


haar_cascade_file_id = '1AXesL4yUQhtDtq6CiERuPBTvIsLNIBrI'
haar_cascade_destination = 'haarcascade_frontalface_alt2.xml'

def check_resources():
    if not path.exists(settings.BASE_DIR+'/'+weight_destination):
        download_weights()
    if not path.exists(settings.BASE_DIR+'/'+haar_cascade_destination):
        download_cascades()
    


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)


def download_weights():
    print("Downloading Weights ...")
    download_file_from_google_drive(weight_file_id, settings.BASE_DIR+'/'+weight_destination)
    print("Weights Downloaded")

def download_cascades():
    print("Downloading Cascades ...")
    download_file_from_google_drive(haar_cascade_file_id, settings.BASE_DIR+'/'+haar_cascade_destination)
    print("Cascades Downloaded")





