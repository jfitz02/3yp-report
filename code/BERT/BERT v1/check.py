#load model_2.h5 and weights_2.h5
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

best_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
best_model = hub.KerasLayer("https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1")

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
preprocessed_text = best_preprocess(text_input)
outputs = best_model(preprocessed_text)

l = tf.keras.layers.Dropout(0.1, name='dropout')(outputs['pooled_output'])
l = tf.keras.layers.Dense(512, activation='relu', name='dense')(l)
l = tf.keras.layers.Dense(26, activation='sigmoid', name='classifier')(l)

model = tf.keras.Model(inputs=[text_input], outputs = [l])
model.load_weights('weights_2.h5')


with open('../topics.txt', 'r') as f:
    categories = f.read().splitlines()

#get userinput for sentence

# sentence = input("Enter a sentence: ")

#predict category

encoder = LabelEncoder()

df = pd.read_csv('./testdata/data.csv', sep=',', names=["Category", "Sentence"])


encoder.fit(df["Category"])

testdata = pd.read_csv('./testdata/data_wiki.csv', sep='\t', names=["Category", "Sentence"])

# test the data on model


while(True):
    sentence = input("Enter a sentence: ")
    prediction = model.predict([sentence])
    #make barchart of confidence for each category
    #need to make sure that the categories are in the same order as the model
    plt.bar(encoder.inverse_transform([i for i in range(len(categories))]), prediction[0])
    plt.xticks(rotation=90)
    plt.tight_layout()
    # plt.show()
    plt.savefig('barchart.png')
    prediction = np.argmax(prediction, axis=1)
    prediction = encoder.inverse_transform(prediction)
    print(prediction)