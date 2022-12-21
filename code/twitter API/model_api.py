import pandas as pd
import datasets
from transformers import RobertaTokenizerFast, RobertaForSequenceClassification, Trainer, TrainingArguments, Wav2Vec2ForCTC, Wav2Vec2Tokenizer
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
        t_data = self.roberta_tokenizer(text, truncation=True, padding=True)
        input_ids = []
        attention_masks = []
        for i in range(len(t_data["input_ids"])):
            input_ids.append(t_data['input_ids'][i])
            attention_masks.append(t_data['attention_mask'][i])

        # convert to tensors
        input_ids = torch.tensor(input_ids)
        attention_masks = torch.tensor(attention_masks)

        # get predictions
        outputs = self.roberta_model(input_ids, attention_mask=attention_masks)
        logits = outputs.logits
        predicted_ids = torch.argmax(logits, dim=-1)
        label = predicted_ids.tolist()

        return label

    def get_topic(self, tweet):
        words = ""
        if False: #if image
            words += self._process_image(tweet)
        if False: #if audio
            words += self._process_audio(tweet)

        words += tweet.text
        return label
