import shutil
import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional
import os
import threading

from pydantic import BaseModel

from chat import chat
from speech_to_text import transcribe
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse

from tts import tts_model
import facedriver 
from stb import SpeechToBlendshape


bs_parser=facedriver.BS_Parser(dataframe_wrapper=facedriver.USC55_to_ARKIT_Wrapper())
face_driver = facedriver.FaceDriver(bs_parser=bs_parser)
stb_model = SpeechToBlendshape()

app = FastAPI()


@app.post("/api/transcribe")
def transcribe_audio(file: UploadFile):
    suffix = Path(file.filename).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        audio_path = Path(tmp.name)
    file.file.close()
    return transcribe(str(audio_path.absolute()))


class ChatWithBotInput(BaseModel):
    conversation_id: Optional[str]
    parent_id: Optional[str]
    message: str


@app.post("/api/chat")
def chat_with_bot(input: ChatWithBotInput):
    response = chat(input.message, input.conversation_id, input.parent_id)
    message = response['message']
    hashed_message = hex(hash(message))[2:]
    response['hash'] = hashed_message
    with open(f'message/{hashed_message}', 'w') as f:
        f.write(message)
    return response


@app.get("/api/tts/{message_hash}")
def message_to_text(message_hash: str):
    filepath = Path(f'./data/{str(message_hash)}.wav').absolute()
    with open(f'message/{message_hash}') as f:
        message = f.read()
    tts_model.to_wav(message, filepath)
    bs_thread = threading.Thread(target=drive_face, args=(message_hash,))
    bs_thread.start()
    return FileResponse(filepath, media_type="audio/wav")


def drive_face(message_hash: str):
    wav_path = Path(f'./data/{str(message_hash)}.wav').absolute()
    result_dir = Path(f'./bs/{str(message_hash)}').absolute()
    os.makedirs(result_dir, exist_ok=True)
    stb_model.to_blendshape(wav_path=wav_path, output_dir=result_dir)
    npy_files = list(result_dir.glob('*.npy'))
    if len(npy_files) != 1:
        print('Blendshape file not found.')
        return
    bs_path = npy_files[0]
    face_driver.send(bs_path=bs_path)