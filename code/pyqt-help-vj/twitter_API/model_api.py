from transformers import AutoTokenizer, AutoModelForSequenceClassification, Wav2Vec2ForCTC, Wav2Vec2Tokenizer, pipeline
import torch
import requests
import librosa
import moviepy.editor as mp
from keras_ocr.detection import Detector
from keras_ocr.pipeline import Pipeline
from keras_ocr.recognition import Recognizer
from keras_ocr.tools import read as kread
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

class TweetProcessor:
    def __init__(self, directory, labels):
        self.labels = labels
        self.directory = directory
        self.topic_tokenizer = AutoTokenizer.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-3")
        self.topic_model = AutoModelForSequenceClassification.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-3")
        self.wav2vec2_tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
        self.wav2vec2_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        self.pipeline = Pipeline(detector=Detector(), recognizer=Recognizer())

    def _process_image(self, image_url):
        # get image
        r = requests.get(image_url)
        with open(f"media_store/jpg/{image_url[-15:-5]}.jpg", "wb") as f:
            f.write(r.content)

        # get test image
        image = kread(f"media_store/jpg/{image_url[-15:-5]}.jpg")
        preds = self.pipeline.recognize(images=[image])[0]
        words = [pred for pred, _ in preds]
        # #turn into string
        words = " ".join(words)

        return words

    def _process_audio(self, audio):
        r = requests.get(audio)
        with open(f"media_store/mp4/{audio[-25:-15]}.mp4", "wb") as f:
            f.write(r.content)

        clip = mp.VideoFileClip(f"media_store/mp4/{audio[-25:-15]}.mp4")
        try:
            clip.audio.write_audiofile(f"media_store/wav/{audio[-25:-15]}.wav")
        except AttributeError as e:
            print("No sound in video")
            return ""

        audio, _ = librosa.load(f"media_store/wav/{audio[-25:-15]}.wav", sr=16000)
        input_values = self.wav2vec2_tokenizer(audio, return_tensors="pt").input_values
        logits = self.wav2vec2_model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.wav2vec2_tokenizer.batch_decode(predicted_ids)[0]

        return transcription

    def _roberta_call(self, text):
        input_ids = self.topic_tokenizer(text, return_tensors="pt")
        output = self.topic_model(**input_ids)
        pred = output.logits.argmax().item()

        return pred

    def get_topic(self, text, image_url=None, audio_url=None):
        words = ""
        if image_url:
            words += self._process_image(image_url)
        if audio_url:
            words += self._process_audio(audio_url)

        words += text

        if len(words) > 512:
            words = words[:512]
        pred = self._roberta_call(words)
        return pred


    def generate_wordcloud(self, text):
        # Create and generate a word cloud image:
        wordcloud = WordCloud(width=335, height=370).generate(text)
        print(os.getcwd())
        # save the wordcloud
        wordcloud.to_file(f"media_store/wordclouds/{text[-10:]}.png")
