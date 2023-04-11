import csv

# TODO: You will want to replace all of the code below. It is just to show you
# an example of reading the CSV files where you will get the data to complete
# the assignment.

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    conversations = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    lines = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]


data = [dict(characters[id],**movies[id]) for id in characters if id in movies]
for character in characters:
    num_of_lines = 0
    for movie in movies:
        if movie["movie_id"] == character["movie_id"]:
            character.update(movie)
    ch_lines = []
    for line in lines:
        if line["movie_id"] == character["movie_id"]:
            ch_lines.append(line)
            if line["character_id"] == character["character_id"]:
                num_of_lines += 1
    character["lines"] = ch_lines
    character["number_of_lines"] = num_of_lines
    convs = []
    for conv in conversations:
        if conv["character1_id"] == character["character_id"] or conv["character2_id"] == character["character_id"]:
            convs.append(conv)
    character["convs"] = convs
    data.append(character)