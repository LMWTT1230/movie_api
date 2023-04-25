from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query

router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_lines(line_id: int):

    line = db.lines.get(line_id)
    if line:
        conv = db.conversations.get(line.conv_id)
        character1 = db.characters.get(conv.c1_id)
        character2 = db.characters.get(conv.c2_id)
        movie = db.movies.get(line.movie_id)
        result = {
            "line_id": line_id,
            "character1": character1.name,
            "character2": character2.name,
            "text": line.line_text,
            "title": movie and movie.title,
        }
        return result

    raise HTTPException(status_code=404, detail="line not found.")


class line_sort_options(str, Enum):
    line_text = "line_text"
    movie_title = "movie_title"
    line_len = "line_len"


# Add get parameters
@router.get("/lines/", tags=["lines"])
def list_movies(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: line_sort_options = line_sort_options.line_text,
):

    if name:

        def filter_fn(l):
            return l.line_text and name in l.line_text

    else:

        def filter_fn(_):
            return True
    items = list(filter(filter_fn, db.lines.values()))

    if sort == line_sort_options.line_text:
        items = [x for x in items if x.line_text]
        items.sort(key=lambda l: l.line_text)
    elif sort == line_sort_options.movie_title:
        items.sort(key=lambda l: db.movies[l.movie_id].title)
    elif sort == line_sort_options.line_len:
        items = [x for x in items if x.line_text]
        items.sort(key=lambda l: len(l.line_text))

    json = (
        {
            "line_id": l.id,
            "character": db.characters[l.c_id].name,
            "text": l.line_text,
            "title": db.movies[l.movie_id].title,
        }
        for l in items[offset : offset + limit]
    )

    return json

@router.get("/conversations/{conversation_id}", tags=["lines"])
def get_dialogue(conversation_id: int):
    conv = db.conversations.get(conversation_id)
    dialogues = []
    if conv:
        character1 = db.characters.get(conv.c1_id)
        character2 = db.characters.get(conv.c2_id)
        for line in db.lines:
            if db.lines[line].conv_id == conversation_id:
                if db.lines[line].c_id == conv.c1_id:
                    dialogues.append(character1.name + " : " + db.lines[line].line_text)
                else:
                    dialogues.append(character2.name + " : " + db.lines[line].line_text)
        movie = db.movies.get(conv.movie_id)
        result = {
            "conversation_id": conversation_id,
            "title": movie and movie.title,
            "character1": character1.name,
            "character2": character2.name,
            "dialogue": dialogues,
        }
        return result

    raise HTTPException(status_code=404, detail="conversation not found.")