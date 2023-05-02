from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query

router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_lines(line_id: int):
    stmt = (
        db.sqlalchemy.text("""
        SELECT line.line_id, character.name, 
        (select name from character where character_id = 
        (select character2_id from conversation where conversation_id = line.conversation_id)) character2, line_text, title
        FROM line
        JOIN movie ON movie.movie_id = line.movie_id 
        JOIN conversation on line.conversation_id = conversation.conversation_id
        JOIN character on line.character_id = character.character_id
        WHERE line_id = :id
        """)
    )

    try:
        with db.engine.connect() as conn:
            json = []
            result = conn.execute(stmt, {"id": line_id})
            for row in result:
                json.append(
                    {
                        "line_id": row.line_id,
                        "character1": row.name,
                        "character2": row.character2,
                        "text" : row.line_text,
                        "title" : row.title
                    }
                )

        return json
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="line not found.")




class line_sort_options(str, Enum):
    line_text = "line_text"
    movie_title = "movie_title"
    character = "character"


# Add get parameters
@router.get("/lines/", tags=["lines"])
def list_movies(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: line_sort_options = line_sort_options.line_text,
):
    if sort is line_sort_options.line_text:
        order_by = db.line.c.line_text
    elif sort is line_sort_options.movie_title:
        order_by = db.movie.c.title
    elif sort is line_sort_options.character:
        order_by = db.character.c.name
    else:
        assert False

    stmt = (
        db.sqlalchemy.select(
            db.line.c.line_id,
            db.character.c.name,
            db.line.c.line_text,
            db.movie.c.title,
        )
            .join(db.movie, db.movie.c.movie_id == db.line.c.movie_id)
            .join(db.character, db.line.c.character_id == db.character.c.character_id)
            .limit(limit)
            .offset(offset)
            .order_by(order_by, db.line.c.line_id)
    )

    # filter only if name parameter is passed
    if name != "":
        stmt = stmt.where(db.line.c.line_text.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "line_id": row.line_id,
                    "character": row.name,
                    "text": row.line_text,
                    "title": row.title,
                }
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