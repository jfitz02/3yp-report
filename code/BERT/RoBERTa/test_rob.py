import pandas as pd

from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-3")

model = AutoModelForSequenceClassification.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-3")

id2labels = {
    0: "music",
    1: "mathematics",
    2: "nature",
    3: "philosophy",
    4: "politics",
    5: "law",
    6: "foods",
    7: "culture",
    8: "science",
    9: "business",
    10: "history",
    11: "videogames",
    12: "disasters",
    13: "geography",
    14: "technology",
    15: "medicine",
    16: "economics",
    17: "entertainment",
    18: "sports",
    19: "religion",
    20: "education",
    21: "news",
    22: "computerscience"
  }

labels2id = {v: k for k, v in id2labels.items()}

# load test data

df = pd.read_csv("../testdata.csv", delimiter=",", header=None, names=["label", "text"])

# loop through each row in the test data

matrix = [[0 for _ in range(len(id2labels))] for _ in range(len(id2labels))]

correct = 0

for index, row in df.iterrows():
    # tokenize the text
    inputs = tokenizer(row["text"], return_tensors="pt")
    outputs = model(**inputs)

    #get the predicted label
    prediction = outputs.logits.argmax().item()

    matrix[prediction][labels2id[row["label"]]] += 1

    correct += 1 if prediction == labels2id[row["label"]] else 0

print("accuracy was " + str(correct/len(df)))

# generate confusion matrix with seaborn

import seaborn as sn

import pandas as pd

import matplotlib.pyplot as plt

df_cm = pd.DataFrame(matrix, index = [i for i in labels2id],
                    columns = [i for i in labels2id])

plt.figure(figsize = (10,7))

sn.heatmap(df_cm, annot=True)

plt.tight_layout()

plt.show()


