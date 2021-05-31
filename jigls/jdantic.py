from os import name
from typing import List, Dict, Optional
from pydantic import BaseModel, create_model, ValidationError, validator
from uuid import UUID
from pprint import pprint

from pydantic import BaseModel as PydanticBaseModel
from pydantic.types import UUID4


class JBaseModel(PydanticBaseModel):
    __slots__ = "__weakref__"

    # class Config:
    #     json_ecoders = {UUID4: lambda v: v.hex}


class JSocketModel(JBaseModel):
    name: str
    uid: UUID4
    nodId: UUID4
    index: int
    type: int
    multiConnection: bool


class JNodeModel(JBaseModel):
    name: str
    uid: UUID4
    socketList: List[JSocketModel]


class JGrNodeModel(JBaseModel):
    node: JNodeModel
    posX: float
    posY: float


class JEdgeModel(JBaseModel):
    uid: UUID4
    startSocket: UUID4
    destnSocket: UUID4


class JGrEdgeModel(JBaseModel):
    edge: JEdgeModel


class JModel(BaseModel):
    nodes: List[Optional[JGrNodeModel]]
    edges: List[Optional[JEdgeModel]]


"""
def TestPydantic():
    nodes = [
        {
            "nodeId": "abd6fc3f882544f5b75661c92fccbd0d",
            "posX": 531.724609375,
            "posY": -975.3916015624995,
            "socketCount": 2,
            "socketInfo": {
                "0": {
                    "socketId": "79977735631c42728339fbc31f911c67",
                    "socketType": 1,
                    "multiConnection": True,
                },
                "1": {
                    "socketId": "681f60634c63490ca583cbc0b2fc773b",
                    "socketType": 2,
                    "multiConnection": False,
                },
            },
        },
    ]
    edges = [
        {
            "edgeId": "1613b0fe65ed40f29c83aef487e33c13",
            "sourceSocketId": "2ee3e89af6f6448eab004e8d5ec3b633",
            "destinationSocketId": "79977735631c42728339fbc31f911c67",
        },
    ]

    o = JModel(nodes=nodes, edges=edges)
    print(o.json(indent=2))
    pprint(o, indent=2)


TestPydantic()
"""


def testparse():
    t = JModel.parse_raw(
        '{"nodes": [{"node": {"name": "base node", "uid": "127f4fbc-e179-427f-b0ee-0bed7c71fb85", "socketList": [{"name": "out1", "uid": "1ac0efd4-e821-4c17-947b-236b83e17965", "nodId": "127f4fbc-e179-427f-b0ee-0bed7c71fb85", "index": 2, "type": 2, "multiConnection": false}, {"name": "in1", "uid": "a6d002e4-d26d-41f7-a487-af762083119c", "nodId": "127f4fbc-e179-427f-b0ee-0bed7c71fb85", "index": 1, "type": 1, "multiConnection": true}]}, "posX": 0.0, "posY": 0.0}, {"node": {"name": "base node", "uid": "1e07daf4-d378-44b4-a101-dfa9913f390b", "socketList": [{"name": "in1", "uid": "053aec7c-0b60-49e4-9368-c6e7a3ec381b", "nodId": "1e07daf4-d378-44b4-a101-dfa9913f390b", "index": 1, "type": 1, "multiConnection": true}, {"name": "out1", "uid": "202150dd-109e-4147-b3c5-56668279a75e", "nodId": "1e07daf4-d378-44b4-a101-dfa9913f390b", "index": 2, "type": 2, "multiConnection": true}]}, "posX": -75.0, "posY": 0.0}, {"node": {"name": "base node", "uid": "0663c3d9-be95-446c-ae9f-3727a043f40f", "socketList": [{"name": "in1", "uid": "db8de379-120e-49af-a8f5-470a749dd17f", "nodId": "0663c3d9-be95-446c-ae9f-3727a043f40f", "index": 1, "type": 1, "multiConnection": false}, {"name": "out1", "uid": "84569970-b392-4c64-8956-e21ef67ab3c1", "nodId": "0663c3d9-be95-446c-ae9f-3727a043f40f", "index": 2, "type": 2, "multiConnection": false}]}, "posX": -350.0, "posY": -250.0}], "edges": []}'
    )

    print(t.dict())
    # print(t.json(indent=2))


# testparse()