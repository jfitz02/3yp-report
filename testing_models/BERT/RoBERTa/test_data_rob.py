from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

data = pd.read_csv("../testdata/test_data.csv", delimiter=",", header=None, names=["label", "text"])

#remove topics "nature" "computerscience" and "news"
data = data[data.label != "nature"]
data = data[data.label != "computerscience"]
data = data[data.label != "news"]
data = data[data.label != "label"]


print(data.label.unique())
# ramdomly sample 50 rows from each topic
data = data.groupby("label").apply(lambda x: x.sample(20, random_state=1)).reset_index(drop=True)

#load tokenizer and model
topic_tokenizer = AutoTokenizer.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-7")
topic_model = AutoModelForSequenceClassification.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-7")

id2label = {
    0: "law",
    1: "geography",
    2: "business",
    3: "economics",
    4: "music",
    5: "foods",
    6: "history",
    7: "medicine",
    8: "mathematics",
    9: "culture",
    10: "disasters",
    11: "science",
    12: "education",
    13: "entertainment",
    14: "politics",
    15: "sports",
    16: "videogames",
    17: "technology",
    18: "religion",
    19: "philosophy"
}

labels2id = { v: k for k, v in id2label.items()}

#test model
incorrect = []
matrix = [[0 for _ in range(len(id2label))] for _ in range(len(id2label))]
correct = 0
i = 0
for index, row in data.iterrows():
    i += 1
    print(i)
    if(len(row["text"]) > 512):
        row["text"] = row["text"][:512]
    inputs = topic_tokenizer(row["text"], return_tensors="pt")
    outputs = topic_model(**inputs)
    prediction = outputs.logits.argmax().item()
    matrix[prediction][labels2id[row["label"]]] += 1
    if row["label"] == id2label[prediction]:
        correct += 1
    else:
        incorrect.append((row["text"], row["label"], id2label[prediction]))

print("accuracy was " + str(correct/len(data)))

for val in incorrect:
    print(val[0])
    print("actual: " + val[1])
    print("predicted: " + val[2])

#draw confusion matrix
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sn

df_cm = pd.DataFrame(matrix, index = [i for i in id2label.values()],
                    columns = [i for i in id2label.values()])
plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True)

plt.show()

