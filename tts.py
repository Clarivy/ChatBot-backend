from espnet2.bin.tts_inference import Text2Speech
from espnet2.utils.types import str_or_none
import torch
from scipy.io.wavfile import write as audio_write
from easydict import EasyDict
import numpy as np
from typing import Optional


class TTS_Model():

    def __init__(self, args) -> None:
        args = EasyDict(args)
        self.args = args

        # Prepare Model
        self.text2speech = Text2Speech.from_pretrained(
            model_tag=str_or_none(args.tag),
            vocoder_tag=str_or_none(args.vocoder_tag),
            device="cuda",
            # Only for Tacotron 2 & Transformer
            threshold=0.5,
            # Only for Tacotron 2
            minlenratio=0.0,
            maxlenratio=10.0,
            use_att_constraint=False,
            backward_window=1,
            forward_window=3,
            # Only for FastSpeech & FastSpeech2 & VITS
            speed_control_alpha=1.0,
            # Only for VITS
            noise_scale=0.333,
            noise_scale_dur=0.333,
        )

    def to_wav(self, text: str, wav_path: Optional[str]):
        sids = np.array(self.args.speaker_id)

        speech = None
        if self.text2speech.use_speech:
            speech = torch.randn(50000, ) * 0.01

        with torch.no_grad():
            wav = self.text2speech(text, speech=speech, sids=sids)["wav"]
        inferred = wav.view(-1).cpu().numpy()
        if wav_path is not None:
            audio_write(wav_path, rate=self.text2speech.fs, data=inferred)

Mandarin_args = {
    'lang': 'Mandarin',
    'tag': 'kan-bayashi/csmsc_full_band_vits', #@param ["kan-bayashi/csmsc_tacotron2", "kan-bayashi/csmsc_transformer", "kan-bayashi/csmsc_fastspeech", "kan-bayashi/csmsc_fastspeech2", "kan-bayashi/csmsc_conformer_fastspeech2", "kan-bayashi/csmsc_vits", "kan-bayashi/csmsc_full_band_vits"] {type: "string"}
    'vocoder_tag': "none", #@param ["none", "parallel_wavegan/csmsc_parallel_wavegan.v1", "parallel_wavegan/csmsc_multi_band_melgan.v2", "parallel_wavegan/csmsc_hifigan.v1", "parallel_wavegan/csmsc_style_melgan.v1"] {type:"string"}
    'speaker_id': 0
}

English_args = {
    'lang': 'English',
    'tag': 'kan-bayashi/vctk_full_band_multi_spk_vits', #@param ["kan-bayashi/vctk_gst_tacotron2", "kan-bayashi/vctk_gst_transformer", "kan-bayashi/vctk_xvector_tacotron2", "kan-bayashi/vctk_xvector_transformer", "kan-bayashi/vctk_xvector_conformer_fastspeech2", "kan-bayashi/vctk_gst+xvector_tacotron2", "kan-bayashi/vctk_gst+xvector_transformer", "kan-bayashi/vctk_gst+xvector_conformer_fastspeech2", "kan-bayashi/vctk_multi_spk_vits", "kan-bayashi/vctk_full_band_multi_spk_vits", "kan-bayashi/libritts_xvector_transformer", "kan-bayashi/libritts_xvector_conformer_fastspeech2", "kan-bayashi/libritts_gst+xvector_transformer", "kan-bayashi/libritts_gst+xvector_conformer_fastspeech2", "kan-bayashi/libritts_xvector_vits"] {type:"string"}
    'vocoder_tag': "none", #@param ["none", "parallel_wavegan/vctk_parallel_wavegan.v1.long", "parallel_wavegan/vctk_multi_band_melgan.v2", "parallel_wavegan/vctk_style_melgan.v1", "parallel_wavegan/vctk_hifigan.v1", "parallel_wavegan/libritts_parallel_wavegan.v1.long", "parallel_wavegan/libritts_multi_band_melgan.v2", "parallel_wavegan/libritts_hifigan.v1", "parallel_wavegan/libritts_style_melgan.v1"] {type:"string"}
    'speaker_id': 5
}

tts_model = TTS_Model(Mandarin_args)
# model.to_wav('Hello!', 'a.wav')