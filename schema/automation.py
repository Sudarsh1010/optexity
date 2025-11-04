from pydantic import BaseModel, model_validator

from schema.actions.assertion_action import AssertionAction
from schema.actions.extraction_action import ExtractionAction
from schema.actions.interaction_action import InteractionAction
from schema.actions.misc_action import PythonScriptAction


class Node(BaseModel):
    index: int
    interaction_action: InteractionAction | None = None
    assertion_action: AssertionAction | None = None
    extraction_action: ExtractionAction | None = None
    python_script_action: PythonScriptAction | None = None

    @model_validator(mode="after")
    def validate_one_node(cls, model: "Node"):
        """Ensure exactly one of the node types is set and matches the type."""
        provided = {
            "interaction_action": model.interaction_action,
            "assertion_action": model.assertion_action,
            "extraction_action": model.extraction_action,
            "python_script_action": model.python_script_action,
        }
        non_null = [k for k, v in provided.items() if v is not None]

        if len(non_null) != 1:
            raise ValueError(
                "Exactly one of interaction_action, assertion_action, extraction_action, or python_script_action must be provided"
            )

        return model


class Automation(BaseModel):
    name: str
    description: str
    nodes: list[Node]
