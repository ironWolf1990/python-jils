# import logging
# from typing import Dict, Optional

# from jigls.jeditor.base.nodebase import JBaseNode
# from jigls.jeditor.constants import JCONSTANTS
# from jigls.jeditor.ui.graphicnode import JGraphicsNode
# from jigls.logger import logger

# logger = logging.getLogger(__name__)


# class JNodeFactory:
#     def __init__(self) -> None:
#         self._nodeRegistry: Dict[str, object] = {}
#         pass

#     @property
#     def nodeRegistry(self):
#         return self._nodeRegistry

#     def RegisterNode(self, name: str, node: object):
#         if name is self._nodeRegistry:
#             logger.warning("node with name already registered")
#             return
#         self._nodeRegistry[name] = node

#     def RegisterNodes(self, nodeDict: Dict[str, object]):
#         for k, v in nodeDict.items():
#             self.RegisterNode(k, v)

#     def CreateRegisteredNode(self, nodeName: str) -> Optional[object]:
#         if nodeName not in self._nodeRegistry:
#             logger.error(f"node name {nodeName} not in registry")
#             return

#         return self._nodeRegistry[nodeName]

#     def CreateGenericNode(self, inputMulti, outputMulti, inputs=2, output=1, *args, **kwargs):

#         base = JBaseNode("base node")
#         for i in range(inputs):
#             base.AddInputSocket(
#                 name=f"in{i}",
#                 multiConnection=inputMulti,
#             )
#         for _ in range(output):
#             base.AddOutputSocket(
#                 name="out1",
#                 multiConnection=outputMulti,
#             )
#         node = JGraphicsNode(base)

#         return node
