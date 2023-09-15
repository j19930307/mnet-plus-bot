from pydantic import BaseModel  # pylint: disable=no-name-in-module


# using FastAPI and Pydantic

class ActionEvent(BaseModel):
    id: str
    trigger: str


class Action(BaseModel):
    event: ActionEvent
