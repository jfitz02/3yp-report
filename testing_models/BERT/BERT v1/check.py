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
l = tf.keras.layers.Dense(20, activation='sigmoid', name='classifier')(l)

model = tf.keras.Model(inputs=[text_input], outputs = [l])
model.load_weights('weights_2.h5')


with open('../../topics.txt', 'r') as f:
    categories = f.read().splitlines()
    mapping = {categories[i].lower():[0 for _ in range(i)]+[1]+[0 for _ in range(len(categories)-(i+1))] for i in range(len(categories))}

df = pd.read_csv('../testdata.csv', sep=',', names=["Category", "Sentence"])

#remove rows whose category is not in categories
df = df[df.Category.isin(categories)]

y_test = np.array([mapping[cat] for cat in df.Category])

X_test = df.Sentence.to_numpy()

# test the data on model

y_pred = model.predict(X_test)

y_pred = np.argmax(y_pred, axis=1)

y_test = np.argmax(y_test, axis=1)

#calculate accuracy
from sklearn.metrics import accuracy_score
print(accuracy_score(y_test, y_pred))

#display confusion matrix
from sklearn.metrics import confusion_matrix
import seaborn as sn

cm = confusion_matrix(y_test, y_pred)

df_cm = pd.DataFrame(cm, index = [i for i in categories],
                    columns = [i for i in categories])
plt.figure(figsize = (10,7))

sn.heatmap(df_cm, annot=True)

#make UI fit to plot

plt.tight_layout()

plt.show()