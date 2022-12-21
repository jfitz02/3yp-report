import pandas as pd
import datasets
from transformers import RobertaTokenizerFast, RobertaForSequenceClassification, Wav2Vec2ForCTC, Wav2Vec2Tokenizer, pipeline
import torch.nn as nn
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from tqdm import tqdm
import os
from keras_ocr.detection import Detector
from keras_ocr.tools import drawAnnotations
from keras_ocr.pipeline import Pipeline
from keras_ocr.recognition import Recognizer
from keras_ocr.tools import read

class TweetProcessor:
    def __init__(self, num_labels:int):
        self.roberta_tokenizer = RobertaTokenizerFast.from_pretrained('roberta-base', max_length = 512)
        self.roberta_model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=num_labels)
        self.wav2vec2_tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
        self.wav2vec2_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        self.pipeline = Pipeline(detector=Detector(), recognizer=Recognizer())

        self.temp_model = pipeline("text-classification", model="jonaskoenig/topic_classification_04",
                                  tokenizer="jonaskoenig/topic_classification_04")

    def _process_image(self, image):
        preds = self.pipeline.recognize(images=[image])
        words = [pred for pred, _ in preds]
        #turn into string
        words = " ".join(words)

        return words

    def _process_audio(self, audio):
        input_values = self.wav2vec2_tokenizer(audio, return_tensors="pt").input_values
        logits = self.wav2vec2_model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.wav2vec2_tokenizer.batch_decode(predicted_ids)[0]

        return transcription

    def _roberta_call(self, text):
        max_label_count = 1
        topicbert = pipeline("text-classification", model="jonaskoenig/topic_classification_04",
                                        tokenizer="jonaskoenig/topic_classification_04")
        top = topicbert(text, top_k=max_label_count)

        return top[0]['label']

    def get_topic(self, tweet):
        words = ""
        if False: #if image
            words += self._process_image(tweet)
        if False: #if audio
            words += self._process_audio(tweet)

        words += tweet.text
        label = self._roberta_call(words)
        return label
