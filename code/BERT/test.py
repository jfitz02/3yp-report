import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import numpy as np

categories = ["Arts", "Culture", "Entertainment",
                "Games", "MassMedia", "Philosophy",
                "Religion", "Science", "Society",
                "Sports", "Technology", "Law",
                "History", "Geography",
                "Esports", "VideoGames", "Music",
                "Medicine", "Business", "PersonalLife",
                "Foods", "Disasters", "Nature",
                "Education", "Statistics"]

#create one hot encoding of categories
encoder = LabelEncoder()

df = pd.read_csv('./testdata/data.csv', sep='\t', names=["Category", "Sentence"])

encoder.fit(df["Category"])
encoded_y = encoder.transform(df["Category"])
dummy_y = to_categorical(encoded_y)


X_train, X_test, y_train, y_test = train_test_split(df.Sentence, dummy_y, test_size=0.2, random_state=42)
#turn elements of y_train and y_test into numpy arrays

best_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
best_model = hub.KerasLayer("https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1")

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
preprocessed_text = best_preprocess(text_input)
outputs = best_model(preprocessed_text)

l = tf.keras.layers.Dropout(0.1, name='dropout')(outputs['pooled_output'])
l = tf.keras.layers.Dense(25, activation='sigmoid', name='classifier')(l)

model = tf.keras.Model(inputs=[text_input], outputs = [l])

[print(i.shape, i.dtype) for i in model.inputs]
print()
[print(o.shape, o.dtype) for o in model.outputs]
print()
print(y_train)
print()
[print(l.name, l.input_shape, l.dtype) for l in model.layers]

input()

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=2, batch_size=32)

print(model.evaluate(X_test, y_test))