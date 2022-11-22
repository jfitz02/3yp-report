import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import numpy as np

categories = ["Culture", "Entertainment",
              "Games", "News", "Philosophy",
              "Religion", "Science",
              "Sports", "Technology", "Law",
              "History", "Geography",
              "Esports", "VideoGames", "Music",
              "Medicine", "Business",
              "Foods", "Disasters", "Nature",
              "Education", "Statistics",
              "Politics", "Economics", "ComputerScience",
              "Mathematics"]

#create one hot encoding of categories
encoder = LabelEncoder()

df = pd.read_csv('./testdata/data.csv', sep=',', names=["Category", "Sentence"])


encoder.fit(df["Category"])
#match encodings to categories
encoded_y = encoder.transform(df["Category"])
#convert to one hot encoding
y = to_categorical(encoded_y)
print(encoded_y)
dummy_y = to_categorical(encoded_y)
print(dummy_y)

X_train, X_test, y_train, y_test = train_test_split(df.Sentence, dummy_y, stratify=dummy_y, test_size=0.2, random_state=42)
#turn elements of y_train and y_test into numpy arrays

best_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
best_model = hub.KerasLayer("https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1")

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
preprocessed_text = best_preprocess(text_input)
outputs = best_model(preprocessed_text)

l = tf.keras.layers.Dropout(0.1, name='dropout')(outputs['pooled_output'])
l = tf.keras.layers.Dense(512, activation='relu', name='dense')(l)
l = tf.keras.layers.Dense(26, activation='sigmoid', name='classifier')(l)

model = tf.keras.Model(inputs=[text_input], outputs = [l])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=6, batch_size=32)

#save model
model.save('model_2.h5')

#save weights
model.save_weights('weights_2.h5')

#display confusion matrix
from sklearn.metrics import confusion_matrix
import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt

y_pred = model.predict(X_test)
y_pred = np.argmax(y_pred, axis=1)
y_test = np.argmax(y_test, axis=1)

cm = confusion_matrix(y_test, y_pred)
df_cm = pd.DataFrame(cm, index = [i for i in categories],
                    columns = [i for i in categories])

plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True)

plt.show()

plt.savefig('confusion_matrix.png')

while(True):
    sentence = input("Enter a sentence: ")
    prediction = model.predict([sentence])
    prediction = np.argmax(prediction, axis=1)
    prediction = encoder.inverse_transform(prediction)
    print(prediction)
