#individually shuffle all csv files in a folder

import os
import csv
import pandas as pd
import random

#fix field larger than field limit (131072)
csv.field_size_limit(524288)

categories = {"Arts":"The arts", "Culture":"Culture", "Entertainment":"Entertainment",
                "Games":"Games", "MassMedia":"Mass media", "Philosophy":"Philosophy",
                "Religion":"Religion", "Science":"Science", "Society":"Society",
                "Sports":"Sports", "Technology":"Technology", "Law":"Law",
                "History":"History", #"Geography":"Geography",
                "Esports":"Esports", "VideoGames":"Video games", "Music":"Music",
                "Medicine":"Medicine", "Business":"Business", "PersonalLife":"Personal life",
                "Foods":"Foods", "Disasters":"Disasters", "Nature":"Nature",
                "Education":"Education", "Statistics":"Statistics"}

for category in categories:
    with open(f"{categories[category]}.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f,delimiter="\n")
        data = []
        for row in reader:
            data.append(row[0])
        random.shuffle(data)
        with open(f"{categories[category]}.csv", "w", encoding="utf-8") as f2:
            for row in data:
                f2.write(f"{row}")
                f2.write("\n")

