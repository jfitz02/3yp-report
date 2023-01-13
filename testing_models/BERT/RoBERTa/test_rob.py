import pandas as pd

from transformers import AutoTokenizer, AutoModelForSequenceClassification

id2label = {
    0: "medicine",
    1: "business",
    2: "videogames",
    3: "education",
    4: "religion",
    5: "science",
    6: "philosophy",
    7: "politics",
    8: "music",
    9: "sports",
    10: "law",
    11: "culture",
    12: "economics",
    13: "geography",
    14: "technology",
    15: "mathematics",
    16: "history",
    17: "foods",
    18: "disasters",
    19: "entertainment"
}

labels2id = { v: k for k, v in id2label.items()}

tokenizer = AutoTokenizer.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5")

model = AutoModelForSequenceClassification.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5", id2label=id2label, label2id=labels2id)


# load test data

df = pd.read_csv("../testdata.csv", delimiter=",", header=None, names=["label", "text"])

#remove rows who's label is not in labels2id

df = df[df.label.isin(labels2id)]

# loop through each row in the test data

matrix = [[0 for _ in range(len(id2label))] for _ in range(len(id2label))]

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


