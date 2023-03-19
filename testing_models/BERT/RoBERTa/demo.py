#load huggingface model

from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5")

model = AutoModelForSequenceClassification.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5")

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

while True:
    text = input("Enter text to classify: ")
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    prediction = outputs.logits.argmax().item()
    print(id2label[prediction])
