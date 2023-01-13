import pandas as pd
import datasets
from transformers import RobertaTokenizerFast, RobertaForSequenceClassification, Trainer, TrainingArguments
import torch.nn as nn
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from tqdm import tqdm
import os

# setup cuda device for training if available, move model into configured device
# device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
# print('Using device:', device)
# print('Using device:', device)

os.environ["WANDB_DISABLED"] = "true"

from huggingface_hub import login

#get token from pass.secret
with open("pass.secret", "r") as f:
    token = f.read()
    token = token.strip()

#login to huggingface
login(token)

# get data and add column names
data = pd.read_csv("../testdata/data_combined_24.csv", delimiter=",", header=None, names=["label", "text"])

#randomly shuffle the data
data = data.sample(frac=1).reset_index(drop=True)

#split into train and test (90/10)
train_data = data[:int(len(data)*0.9)]
test_data = data[int(len(data)*0.9)+1:]

model = RobertaForSequenceClassification.from_pretrained('roberta-base')
tokenizer = RobertaTokenizerFast.from_pretrained('roberta-base', max_length = 512)

# tokenize the data adding padding so that all sequences are the same length
t_train_data = tokenizer(train_data.text.tolist(), truncation=True, padding=True)
t_test_data = tokenizer(test_data.text.tolist(), truncation=True, padding=True)


# get all input_ids
train_input_ids = []
train_attention_masks = []
for i in range(len(t_train_data["input_ids"])):
    train_input_ids.append(t_train_data['input_ids'][i])
    train_attention_masks.append(t_train_data['attention_mask'][i])

# check all input_ids are the same length
for i in range(len(train_input_ids)):
    if len(train_input_ids[i]) != 512:
        print("Error: input_ids not 512")

# check all attention_masks are the same length
for i in range(len(train_attention_masks)):
    if len(train_attention_masks[i]) != 512:
        print("Error: attention_masks not 512")

test_input_ids = []
test_attention_masks = []

for i in range(len(t_test_data["input_ids"])):
    test_input_ids.append(t_test_data['input_ids'][i])
    test_attention_masks.append(t_test_data['attention_mask'][i])

# check all input_ids are the same length
for i in range(len(test_input_ids)):
    if len(test_input_ids[i]) != 512:
        print("Error: input_ids not 512")

# check all attention_masks are the same length
for i in range(len(test_attention_masks)):
    if len(test_attention_masks[i]) != 512:
        print("Error: attention_masks not 512")

# get all unique topics
topics = data['label'].unique()

# create mapping from topic to integer
topic_to_int = {}
for i in range(len(topics)):
    topic_to_int[topics[i]] = i

# create mapping from integer to topic
int_to_topic = {}
for i in range(len(topics)):
    int_to_topic[i] = topics[i]

# train_data.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
# test_data.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])

# create np array combining input_ids and attention_mask and label
train_data_np = np.array([train_input_ids, train_attention_masks, train_data['label']]).T
test_data_np = np.array([test_input_ids, test_attention_masks, test_data['label']]).T

final_train = pd.DataFrame(train_data_np, columns=['input_ids', 'attention_mask', 'label'])

final_test = pd.DataFrame(test_data_np, columns=['input_ids', 'attention_mask', 'label'])

# map label to integer
if type(final_train['label'][0]) == str:
    final_train['label'] = final_train['label'].map(lambda x: topic_to_int[x])

if type(final_test['label'][0]) == str:
    final_test['label'] = final_test['label'].map(lambda x: topic_to_int[x])


dataframe_train = datasets.Dataset.from_pandas(final_train)
dataframe_test = datasets.Dataset.from_pandas(final_test)


def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='macro')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

training_args = TrainingArguments(
    f"roberta-finetuned-topic",
    evaluation_strategy = "epoch",
    save_strategy = "epoch",
    learning_rate=2e-5,
    per_gpu_train_batch_size=4,
    per_gpu_eval_batch_size=4,
    num_train_epochs=5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    push_to_hub=True,
)

trainer = Trainer(
    model,
    training_args,
    train_dataset=dataframe_train,
    eval_dataset=dataframe_test,
    # tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()