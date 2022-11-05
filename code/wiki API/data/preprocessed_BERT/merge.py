#merge all csv's in directoy into new csv data.csv

import os
import csv
import pandas as pd

#fix field larger than field limit (131072)
csv.field_size_limit(524288)

categories = {"Arts":"The arts", "Culture":"Culture", "Entertainment":"Entertainment",
                "Games":"Games", "MassMedia":"Mass media", "Philosophy":"Philosophy",
                "Religion":"Religion", "Science":"Science", "Society":"Society",
                "Sports":"Sports", "Technology":"Technology", "Law":"Law",
                "History":"History", "Geography":"Geography",
                "Esports":"Esports", "VideoGames":"Video games", "Music":"Music",
                "Medicine":"Medicine", "Business":"Business", "PersonalLife":"Personal life",
                "Foods":"Foods", "Disasters":"Disasters", "Nature":"Nature",
                "Education":"Education", "Statistics":"Statistics"}

with open("data.csv", "w", encoding="utf-8") as f:
    for category in categories:
        with open(f"{categories[category]}.csv", "r", encoding="utf-8") as f2:
            reader = csv.reader(f2,delimiter="\n")
            for row in reader:
                f.write(f"{row[0]}")
                f.write("\n")

