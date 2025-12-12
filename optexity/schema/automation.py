import logging
from typing import Annotated, Any, ForwardRef, Literal

from pydantic import BaseModel, Field, model_validator

from optexity.schema.actions.assertion_action import AssertionAction
from optexity.schema.actions.extraction_action import ExtractionAction
from optexity.schema.actions.interaction_action import InteractionAction
from optexity.schema.actions.misc_action import PythonScriptAction
from optexity.schema.actions.two_factor_auth_action import Fetch2faAction
from optexity.utils.utils import get_onepassword_value, get_totp_code

logger = logging.getLogger(__name__)


class OnePasswordParameter(BaseModel):
    vault_name: str
    item_name: str
    field_name: str
    type: Literal["raw", "totp_secret"] = "raw"
    digits: int | None = None

    @model_validator(mode="after")
    def validate_onepassword_parameter(self):
        if self.type == "totp_secret":
            assert self.digits is not None, "digits must be provided for totp_secret"
        else:
            assert self.digits is None, "digits must not be provided for raw"
        return self


class AmazonSecretsManagerParameter(BaseModel):
    pass

    @model_validator(mode="after")
    def validate_amazon_secrets_manager_parameter(
        cls, model: "AmazonSecretsManagerParameter"
    ):
        raise NotImplementedError("Amazon Secrets Manager is not implemented yet")


class TOTPParameter(BaseModel):
    totp_secret: str
    digits: int = 6


class SecureParameter(BaseModel):
    onepassword: OnePasswordParameter | None = None
    amazon_secrets_manager: AmazonSecretsManagerParameter | None = None
    totp: TOTPParameter | None = None

    @model_validator(mode="after")
    def validate_secure_parameter(self):
        non_null = [k for k, v in self.model_dump().items() if v is not None]
        if len(non_null) != 1:
            raise ValueError(
                "Exactly one of onepassword or amazon_secrets_manager or totp must be provided"
            )
        return self


class ActionNode(BaseModel):
    type: Literal["action_node"]
    interaction_action: InteractionAction | None = None
    assertion_action: AssertionAction | None = None
    extraction_action: ExtractionAction | None = None
    python_script_action: PythonScriptAction | None = None
    fetch_2fa_action: Fetch2faAction | None = None
    before_sleep_time: float = 0.0
    end_sleep_time: float = 3.0
    expect_new_tab: bool = False
    max_new_tab_wait_time: float = 0.0

    @model_validator(mode="after")
    def validate_one_node(cls, model: "ActionNode"):
        """Ensure exactly one of the node types is set and matches the type."""
        provided = {
            "interaction_action": model.interaction_action,
            "assertion_action": model.assertion_action,
            "extraction_action": model.extraction_action,
            "python_script_action": model.python_script_action,
            "fetch_2fa_action": model.fetch_2fa_action,
        }
        non_null = [k for k, v in provided.items() if v is not None]

        if len(non_null) != 1:
            raise ValueError(
                "Exactly one of interaction_action, assertion_action, extraction_action, python_script_action, or fetch_2fa_action must be provided"
            )

        assert (
            model.end_sleep_time >= 0 and model.end_sleep_time <= 10
        ), "end_sleep_time must be greater than 0 and less than 10"
        assert (
            model.max_new_tab_wait_time >= 0 and model.max_new_tab_wait_time <= 10
        ), "max_new_tab_wait_time must be greater than 0 and less than 10"

        # --- Adjust defaults only if user didn't override them ---
        # We detect user-provided fields using model.__pydantic_fields_set__
        user_set = model.__pydantic_fields_set__

        if "end_sleep_time" not in user_set:
            model.end_sleep_time = (
                0.0
                if model.assertion_action
                or model.extraction_action
                or model.fetch_2fa_action
                else 1.0
            )

        if "before_sleep_time" not in user_set:
            model.before_sleep_time = 3.0 if model.extraction_action else 0.0

        if model.expect_new_tab:
            assert (
                model.interaction_action is not None
            ), "expect_new_tab is only allowed for interaction actions"
            model.max_new_tab_wait_time = 10.0
        else:
            model.max_new_tab_wait_time = 0.0

        return model

    def replace(self, pattern: str, replacement: str | int | float | bool | None):
        replacement = str(replacement)
        if self.interaction_action:
            self.interaction_action.replace(pattern, replacement)
        if self.assertion_action:
            self.assertion_action.replace(pattern, replacement)
        if self.extraction_action:
            self.extraction_action.replace(pattern, replacement)
        if self.python_script_action:
            pass
        if self.fetch_2fa_action:
            pass

        return self

    async def replace_variables(
        self, variables: dict[str, list[str | SecureParameter]]
    ):
        for key, values in variables.items():

            for index, value in enumerate(values):
                pattern = f"{{{key}[{index}]}}"

                if isinstance(value, SecureParameter):
                    if value.onepassword:
                        str_value = await get_onepassword_value(
                            value.onepassword.vault_name,
                            value.onepassword.item_name,
                            value.onepassword.field_name,
                        )
                        if value.onepassword.type == "totp_secret":
                            str_value = get_totp_code(
                                str_value, value.onepassword.digits
                            )

                    elif value.amazon_secrets_manager:
                        raise NotImplementedError(
                            "Amazon Secrets Manager is not implemented yet"
                        )
                    elif value.totp:
                        str_value = get_totp_code(
                            value.totp.totp_secret, value.totp.digits
                        )

                elif isinstance(value, str):
                    str_value = value
                else:
                    raise ValueError(f"Invalid value type for {key}: {type(value)}")

                self.replace(pattern, str_value)

        return self


class ForLoopNode(BaseModel):
    # Loops through range of values of {variable_name[index]}
    type: Literal["for_loop_node"]
    variable_name: str
    nodes: list[ActionNode]

    @model_validator(mode="before")
    def migrate_old_nodes(cls, data: dict[str, Any]):
        for key in ["nodes"]:
            raw_nodes = data.get(key, [])
            new_nodes = []
            used_old_format = False

            for item in raw_nodes:
                if (
                    isinstance(item, ActionNode)
                    or isinstance(item, ForLoopNode)
                    or isinstance(item, IfElseNode)
                ):
                    new_nodes.append(item)
                    continue

                # --- new format: already has a type ---
                if isinstance(item, dict) and "type" in item:
                    new_nodes.append(item)
                    continue

                # --- old format cases ---
                used_old_format = True

                if isinstance(item, dict) and "condition" in item:
                    new_nodes.append({"type": "if_else_node", **item})
                    continue

                if isinstance(item, dict) and "variable_name" in item:
                    new_nodes.append({"type": "for_loop_node", **item})
                    continue

                new_nodes.append({"type": "action_node", **item})

            if used_old_format:
                logger.warning(
                    "Old node format without 'type' is deprecated. "
                    "Use the new format: {'type': 'action_node'|'for_loop_node'|'if_else_node', ...}"
                )

            data[key] = new_nodes
        return data


IfElseNodeRef = ForwardRef("IfElseNode")


class IfElseNode(BaseModel):
    type: Literal["if_else_node"]
    condition: str
    if_nodes: list[ActionNode | IfElseNodeRef]
    else_nodes: list[ActionNode | IfElseNodeRef] = []

    @model_validator(mode="before")
    def migrate_old_nodes(cls, data: dict[str, Any]):
        for key in ["if_nodes", "else_nodes"]:
            raw_nodes = data.get(key, [])
            new_nodes = []
            used_old_format = False

            for item in raw_nodes:
                if (
                    isinstance(item, ActionNode)
                    or isinstance(item, ForLoopNode)
                    or isinstance(item, IfElseNode)
                ):
                    new_nodes.append(item)
                    continue

                # --- new format: already has a type ---
                if isinstance(item, dict) and "type" in item:
                    new_nodes.append(item)
                    continue

                # --- old format cases ---
                used_old_format = True

                if isinstance(item, dict) and "condition" in item:
                    new_nodes.append({"type": "if_else_node", **item})
                    continue

                if isinstance(item, dict) and "variable_name" in item:
                    new_nodes.append({"type": "for_loop_node", **item})
                    continue

                new_nodes.append({"type": "action_node", **item})

            if used_old_format:
                logger.warning(
                    "Old node format without 'type' is deprecated. "
                    "Use the new format: {'type': 'action_node'|'for_loop_node'|'if_else_node', ...}"
                )

            data[key] = new_nodes
        return data


class Parameters(BaseModel):
    input_parameters: dict[str, list[str | int | float | bool]]
    secure_parameters: dict[str, list[SecureParameter]] = Field(default_factory=dict)
    generated_parameters: dict[str, list[str | int | float | bool | None]]


class Automation(BaseModel):
    browser_channel: Literal["chromium", "chrome"] = "chromium"
    expected_downloads: int = 0
    url: str
    parameters: Parameters
    nodes: list[
        Annotated[ActionNode | ForLoopNode | IfElseNode, Field(discriminator="type")]
    ]

    @model_validator(mode="before")
    def migrate_old_nodes(cls, data: dict[str, Any]):
        raw_nodes = data.get("nodes", [])
        new_nodes = []
        used_old_format = False

        for item in raw_nodes:
            if (
                isinstance(item, ActionNode)
                or isinstance(item, ForLoopNode)
                or isinstance(item, IfElseNode)
            ):
                new_nodes.append(item)
                continue

            # --- new format: already has a type ---
            if isinstance(item, dict) and "type" in item:
                new_nodes.append(item)
                continue

            # --- old format cases ---
            used_old_format = True

            if isinstance(item, dict) and "condition" in item:
                new_nodes.append({"type": "if_else_node", **item})
                continue

            if isinstance(item, dict) and "variable_name" in item:
                new_nodes.append({"type": "for_loop_node", **item})
                continue

            new_nodes.append({"type": "action_node", **item})

        if used_old_format:
            logger.warning(
                "Old node format without 'type' is deprecated. "
                "Use the new format: {'type': 'action_node'|'for_loop_node'|'if_else_node', ...}"
            )

        data["nodes"] = new_nodes
        return data

    @model_validator(mode="after")
    def validate_parameters_with_examples(cls, model: "Automation"):
        ## TODO: static check that all parameters with examples are used in the nodes
        return model
