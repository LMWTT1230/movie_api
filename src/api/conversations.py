from fastapi import APIRouter
from src import database as db
from pydantic import BaseModel
from typing import List


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """

    if db.characters.get(conversation.character_1_id).movie_id == movie_id and db.characters.get(conversation.character_2_id).movie_id == movie_id and conversation.character_1_id != conversation.character_2_id:
        id = max(db.conversations.keys()) + 1
        conv_dict = {"conversation_id": id, "character1_id": conversation.character_1_id, "character2_id": conversation.character_2_id, "movie_id": movie_id}
        db.lst_convs.append(conv_dict)
        db.update_convs(conv_dict)
        line_id = max(db.lines.keys()) + 1
        print(conversation.lines)
        for i in range(len(conversation.lines)):
            line_dict = {"line_id": line_id + i,"character_id": conversation.lines[i].character_id, "movie_id": movie_id, "conversation_id": id, "line_sort": i+1, "line_text": conversation.lines[i].line_text}
            db.lst_lines.append(line_dict)
            db.update_lines(line_dict)
        db.upload_new_conv()
        db.upload_new_line()
        return id