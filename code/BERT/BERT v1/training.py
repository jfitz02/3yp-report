import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import numpy as np

with open('../topics.txt', 'r') as f:
    categories = f.read().splitlines()
    mapping = {categories[i].lower():[0 for _ in range(i)]+[1]+[0 for _ in range(len(categories)-(i+1))] for i in range(len(categories))}

print(mapping)
df = pd.read_csv('./testdata/data.csv', sep=',', names=["Category", "Sentence"])

y_train = np.array([mapping[cat] for cat in df.Category])


X_train = df.Sentence.to_numpy()
#turn elements of y_train and y_test into numpy arrays

best_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
best_model = hub.KerasLayer("https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1")

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
preprocessed_text = best_preprocess(text_input)
outputs = best_model(preprocessed_text)

l = tf.keras.layers.Dropout(0.1, name='dropout')(outputs['pooled_output'])
l = tf.keras.layers.Dense(len(categories), activation='sigmoid', name='classifier')(l)

model = tf.keras.Model(inputs=[text_input], outputs = [l])

# model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# model.fit(X_train, y_train, epochs=6, batch_size=32)

# #save model
# model.save('model_2.h5')

# #save weights
# model.save_weights('weights_2.h5')

model.load_weights('weights_2.h5')

#display confusion matrix
from sklearn.metrics import confusion_matrix
import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt

#get train data from ./testdata/data_wiki.csv
df = pd.read_csv('./testdata/data_wiki.csv', sep='\t', names=["Category", "Sentence"])

x_test = df.Sentence.to_numpy()
y_test = np.array([mapping[cat.lower()] for cat in df.Category])

y_pred = model.predict(x_test)
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
    
    #get key where value is equal to prediction
    for key, value in mapping.items():
        if value == prediction:
            print(key)
            break
    print(prediction)
