import wikipediaapi as wiki
import csv
import random

my_wiki = wiki.Wikipedia('en')

def get_category_members(category, level=0, max_level=1):
    cat = my_wiki.page(f"Category:{category}")
    titles = []
    for i, c in enumerate(cat.categorymembers.values()):
        if c.title.startswith("Category:") and level < max_level:
            new_titles = get_category_members(c.title[9:], level=level+1, max_level=max_level)
            titles.extend(new_titles)
        elif not c.title.startswith("Category:"):
            titles.append(c.title)
        else:
            pass
    
    try:
        titles = random.sample(titles, 100)
    except ValueError as e:
        titles = titles

    return titles

categories = ["The arts", "Culture", "Entertainment",
              "Games", "Mass media", "Philosophy",
              "Religion", "Science", "Society",
              "Sports", "Technology", "Law",
              "History", "Geography",
              "Esports", "Video games", "Music",
              "Medicine", "Business", "Personal life",
              "Foods", "Disasters", "Nature",
              "Education", "Statistics"]

for category in categories:
    titles = get_category_members(category)
    with open(f"./data/raw/{category}.csv", "a", newline="", encoding="utf-8") as f:
        total_text = ""
        for title in titles:
            page = my_wiki.page(title)
            # print(page.text)
            text = page.text
            if page.text == "":
                text = page.summary
            if text == "":
                continue
            #change text to all be one line
            text = text.replace("\n", " ")
            total_text += text+"\n"
            
        f.write(f"{total_text}")