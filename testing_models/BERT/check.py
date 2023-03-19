import numpy as np
#import for huggingface transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification

#load tokenizer and model
topic_tokenizer = AutoTokenizer.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5")
topic_model = AutoModelForSequenceClassification.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5")


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

while(True):
    sentence = input("Enter a sentence: ")
    input_ids = topic_tokenizer(sentence, return_tensors="pt")
    output = topic_model(**input_ids)
    prediction = np.argmax(output.logits.detach().numpy())
    

    print(id2label[prediction])