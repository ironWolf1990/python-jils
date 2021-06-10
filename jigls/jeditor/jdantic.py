from os import name
from typing import Any, Callable, List, Dict, Optional
from pydantic import BaseModel, create_model, ValidationError, validator
from uuid import UUID
from pprint import pprint

from pydantic import BaseModel as PydanticBaseModel

# from pydantic.types import UUID4


class JBaseModel(PydanticBaseModel):
    __slots__ = "__weakref__"

    # class Config:
    #     json_ecoders = {UUID4: lambda v: v.hex}


class JSocketModel(JBaseModel):
    name: str
    uid: str
    type: int
    multiConnect: bool
    dataType: str
    default: Optional[Any]
    exec: bool
    execOnChange: bool
    execOnConnect: bool
    monitorOnChange: bool
    traceback: bool


class JNodeModel(JBaseModel):
    name: str
    uid: str
    socketList: List[JSocketModel]


class JGrNodeModel(JBaseModel):
    node: JNodeModel
    posX: float
    posY: float


class JGrEdgeModel(JBaseModel):
    uid: str
    startSocket: str
    destnSocket: str
    pathType: int


# class JGrEdgeModel(JBaseModel):
#     edge: JEdgeModel


class JModel(BaseModel):
    nodes: List[Optional[JGrNodeModel]]
    edges: List[Optional[JGrEdgeModel]]