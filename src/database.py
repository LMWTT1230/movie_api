import csv
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

# Reading in the log file from the supabase bucket
log_conv_csv = (
    supabase.storage.from_("movie-api")
        .download("conversations.csv")
        .decode("utf-8")
)
lst_convs = []
for row in csv.DictReader(io.StringIO(log_conv_csv), skipinitialspace=True):
    lst_convs.append(row)

log_line_csv = (
    supabase.storage.from_("movie-api")
        .download("lines.csv")
        .decode("utf-8")
)
lst_lines = []
for row in csv.DictReader(io.StringIO(log_line_csv), skipinitialspace=True):
    lst_lines.append(row)

# Writing to the log file and uploading to the supabase bucket
def upload_new_conv():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["conversation_id", "character1_id", "character2_id", "movie_id"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(lst_convs)
    supabase.storage.from_("movie-api").upload(
        "conversations.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )

def upload_new_line():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["line_id", "character_id", "movie_id", "conversation_id", "line_sort", "line_text"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(lst_lines)
    supabase.storage.from_("movie-api").upload(
        "lines.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )


def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None


with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = {
        try_parse(int, row["movie_id"]): Movie(
            try_parse(int, row["movie_id"]),
            row["title"] or None,
            row["year"] or None,
            try_parse(float, row["imdb_rating"]),
            try_parse(int, row["imdb_votes"]),
            row["raw_script_url"] or None,
        )
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    }

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        char = Character(
            try_parse(int, row["character_id"]),
            row["name"] or None,
            try_parse(int, row["movie_id"]),
            row["gender"] or None,
            try_parse(int, row["age"]),
            0,
        )
        characters[char.id] = char


conversations = {}
for item in lst_convs:
    conv = Conversation(
        try_parse(int, item["conversation_id"]),
        try_parse(int, item["character1_id"]),
        try_parse(int, item["character2_id"]),
        try_parse(int, item["movie_id"]),
        0,
    )
    conversations[conv.id] = conv


lines = {}
for item in lst_lines:
    line = Line(
        try_parse(int, item["line_id"]),
        try_parse(int, item["character_id"]),
        try_parse(int, item["movie_id"]),
        try_parse(int, item["conversation_id"]),
        try_parse(int, item["line_sort"]),
        item["line_text"],
    )
    lines[line.id] = line
    c = characters.get(line.c_id)
    if c:
        c.num_lines += 1

    conv = conversations.get(line.conv_id)
    if conv:
        conv.num_lines += 1

def update_convs(conv_dict):
    conv = Conversation(
        try_parse(int, conv_dict["conversation_id"]),
        try_parse(int, conv_dict["character1_id"]),
        try_parse(int, conv_dict["character2_id"]),
        try_parse(int, conv_dict["movie_id"]),
        0,
    )
    conversations[conv.id] = conv

def update_lines(line_dict):
    line = Line(
        try_parse(int, line_dict["line_id"]),
        try_parse(int, line_dict["character_id"]),
        try_parse(int, line_dict["movie_id"]),
        try_parse(int, line_dict["conversation_id"]),
        try_parse(int, line_dict["line_sort"]),
        line_dict["line_text"],
    )
    lines[line.id] = line
    c = characters.get(line.c_id)
    if c:
        c.num_lines += 1

    conv = conversations.get(line.conv_id)
    if conv:
        conv.num_lines += 1
