from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: str):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
    json = None
    name1 = None
    gender1 = None
    title = None
    sorted_list = None
    exist = False
    for character in db.characters:
        if character["character_id"] == id:
            exist = True
            name1 = character["name"]
            if character["gender"] != "":
                gender1 = character["gender"]
            for movie in db.movies:
                if movie["movie_id"] == character["movie_id"]:
                    title = movie["title"]
            ls_conv = []
            for conv in db.conversations:
                dict = None
                name2 = None
                gender2 = None
                exist1 = False
                if conv["character1_id"] == id:
                    id2 = conv["character2_id"]
                elif conv["character2_id"] == id:
                    id2 = conv["character1_id"]
                else:
                    continue
                for item in ls_conv:
                    if item["character_id"] == id2:
                        exist1 = True
                        dict = item
                if not exist1:
                    for c in db.characters:
                        if c["character_id"] == id2:
                            name2 = c["name"]
                            if c["gender"] != "":
                                gender2 = c["gender"]
                    conversation = {'character_id': id2, 'character': name2, 'gender': gender2, 'number_of_lines_together': 0}
                    dict = conversation
                    ls_conv.append(conversation)
                for line in db.lines:
                    if line["conversation_id"] == conv["conversation_id"]:
                        dict["number_of_lines_together"] += 1

            sorted_list = sorted(ls_conv, key=lambda k: k["number_of_lines_together"], reverse= True)

    if exist:
        json = {
            "character_id": id,
            "character": name1,
            "movie": title,
            "gender": gender1,
            "top_conversations": sorted_list,
        }


    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")

    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    lst = []
    for character in db.characters:
        num_of_lines = 0
        title = None
        if character["name"] == "":
            continue
        if name != "" and name.upper() not in character["name"]:
            continue
        for movie in db.movies:
            if movie["movie_id"] == character["movie_id"]:
                title = movie["title"]
        for line in db.lines:
            if line["character_id"] == character["character_id"] and line["movie_id"] == character["movie_id"]:
                num_of_lines += 1
        charc = {"character_id": character["character_id"], "character": character["name"], "movie": title, "number_of_lines": num_of_lines}
        lst.append(charc)
    sorted_list = sorted(lst, key=lambda k: k[sort.name])
    if sort.name == "number_of_lines":
        sorted_list.reverse()
    json = sorted_list[offset:limit+offset]

    return json
