from typing import Optional
from PyQt5.QtCore import QPointF

from PyQt5.QtWidgets import QGraphicsItem
from jigls.jeditor.jdantic import JGrNodeModel
from jigls.jeditor.base.nodebase import JBaseNode
from jigls.jeditor.ui.graphicnode import JGraphicsNode


class WebElementNode(JGraphicsNode):

    __TYPE__: str = "WebElement"

    def __init__(self, baseNode: JBaseNode, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(baseNode, parent=parent)

        self.AddInputSocket("in1", True)
        self.AddOutputSocket("out1", True)

        self.dataContent.AddComboBox(label="Group", options=[str(x + 1) for x in range(10)])
        self.dataContent.AddComboBox(
            label="Element Type", options=["Dropdown", "Text", "Checkbox", "RadioButton", "RadioCheckbox"]
        )
        self.dataContent.AddTextEdit(label="Description", placeholder="dummy description ...")
        self.dataContent.AddSectionTree(label="XPath", sectionName="XPath")
        self.dataContent.AddSectionTree(label="Value", sectionName="Value")
        self.dataContent.AddLineEdit(label="Action", placeholder="action ...")

        self.baseNode.exec = False


class Action(JGraphicsNode):

    __TYPE__: str = "Action"

    def __init__(self, baseNode: JBaseNode, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(baseNode, parent=parent)

        self.AddInputSocket("in1", True)
        self.AddOutputSocket("out1", True)

        self.dataContent.AddComboBox(label="Group", options=["Button", "Function", "Link"])
        self.dataContent.AddLineEdit(label="Value", placeholder="action ...")
        self.dataContent.AddLineEdit(label="Action", placeholder="action ...")

        self.baseNode.exec = False


class EnableNode(JGraphicsNode):
    __TYPE__: str = "EnableNode"

    def __init__(self, baseNode: JBaseNode, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(baseNode, parent=parent)

        self.AddInputSocket("in1", True)
        self.AddOutputSocket("out1", True)

        self.dataContent.AddSectionTree(label="Value", sectionName="Value")

        self.baseNode.exec = False


class DisableNode(JGraphicsNode):
    __TYPE__: str = "DisableNode"

    def __init__(self, baseNode: JBaseNode, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(baseNode, parent=parent)

        self.AddInputSocket("in1", True)
        self.AddOutputSocket("out1", True)

        self.dataContent.AddSectionTree(label="Value", sectionName="Value")

        self.baseNode.exec = False
