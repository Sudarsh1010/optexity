from optexity.schema.actions.assertion_action import AssertionAction
from optexity.schema.actions.extraction_action import ExtractionAction
from optexity.schema.actions.interaction_action import InteractionAction
from optexity.schema.actions.misc_action import PythonScriptAction
from pydantic import BaseModel, model_validator


class ActionNode(BaseModel):
    interaction_action: InteractionAction | None = None
    assertion_action: AssertionAction | None = None
    extraction_action: ExtractionAction | None = None
    python_script_action: PythonScriptAction | None = None
    end_sleep_time: float = 1.0

    @model_validator(mode="after")
    def validate_one_node(cls, model: "ActionNode"):
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

        assert model.end_sleep_time > 0, "end_sleep_time must be greater than 0"

        return model

    def replace(self, pattern: str, replacement: str):
        if self.interaction_action:
            self.interaction_action.replace(pattern, replacement)
        if self.assertion_action:
            raise NotImplementedError(
                "Assertion replacement function is not implemented"
            )
        if self.extraction_action:
            raise NotImplementedError(
                "Extraction replacement function is not implemented"
            )
        if self.python_script_action:
            raise NotImplementedError(
                "Python script replacement function is not implemented"
            )

        return self

    def replace_variables(self, variables: dict[str, list[str]]):
        for key, values in variables.items():
            for index, value in enumerate(values):
                pattern = f"{{{key}[{index}]}}"
                self.replace(pattern, value)

        return self


class ForLoopNode(BaseModel):
    # Loops through range of values of {variable_name[index]}
    variable_name: str
    nodes: list[ActionNode]


class Automation(BaseModel):
    name: str
    description: str
    nodes: list[ActionNode | ForLoopNode]
