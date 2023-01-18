import whisper

models = {}


def transcribe(audio_file_path: str, model_name: str = "base"):
    if model_name not in models:
        models[model_name] = whisper.load_model(model_name)
    model = models[model_name]
    return model.transcribe(audio_file_path)
