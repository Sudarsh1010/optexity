from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator


class LLMAssertion(BaseModel):
    source: list[Literal["axtree", "screenshot"]]
    output_format: str | BaseModel
    extraction_instruction: str
    ## TODO: add output to memory variables


class NetworkCallAssertion(BaseModel):
    url_pattern: Optional[str] = None
    header_filter: Optional[dict[str, str]] = None


class PythonScriptAssertion(BaseModel):
    script: str
    ## TODO: add output to memory variables

    @field_validator("script")
    @classmethod
    def validate_script(cls, v: str):
        if not v.strip():
            raise ValueError("Script cannot be empty")
        return v


class AssertionAction(BaseModel):
    network_call: Optional[NetworkCallAssertion] = None
    llm: Optional[LLMAssertion] = None
    python_script: Optional[PythonScriptAssertion] = None

    @model_validator(mode="after")
    def validate_one_assertion(cls, model: "AssertionAction"):
        """Ensure exactly one of the extraction types is set and matches the type."""
        provided = {
            "llm": model.llm,
            "network_call": model.network_call,
            "python_script": model.python_script,
        }
        non_null = [k for k, v in provided.items() if v is not None]

        if len(non_null) != 1:
            raise ValueError(
                "Exactly one of llm, networkcall, or python must be provided"
            )

        return model
