#merge all csv's in directoy into new csv data.csv

import os
import csv
import pandas as pd

#fix field larger than field limit (131072)
csv.field_size_limit(524288)

with open("../../../topics.txt", "r") as f:
    categories = f.read().split("\n")

with open("data.csv", "w", encoding="utf-8") as f:
    for category in categories:
        with open(f"{category}.csv", "r", encoding="utf-8") as f2:
            reader = csv.reader(f2,delimiter="\n")
            i = 0
            for row in reader:
                f.write(f"{row[0]}")
                f.write("\n")
                i+=1
                if i > 1000:
                    break

