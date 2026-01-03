from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from optexity.schema.automation import SecureParameter


class InferenceRequest(BaseModel):
    endpoint_name: str
    input_parameters: dict[str, list[str | int | float | bool]]
    unique_parameter_names: list[str] = Field(default_factory=list)
    secure_parameters: dict[str, list[SecureParameter]] = Field(default_factory=dict)
    use_proxy: bool = False

    @model_validator(mode="after")
    def validate_unique_parameter_names(self):
        for unique_parameter_name in self.unique_parameter_names:
            if unique_parameter_name not in self.input_parameters and (
                self.secure_parameters is None
                or unique_parameter_name not in self.secure_parameters
            ):
                raise ValueError(
                    f"unique_parameter_name {unique_parameter_name} not found in input_parameters or secure_parameters"
                )
        return self


class FetchEmailTwoFARequest(BaseModel):
    receiver_email_address: str  # receiver's email address
    sender_email_address: str  # sender's email address
    start_2fa_time: datetime
    end_2fa_time: datetime

    @model_validator(mode="after")
    def validate_time_parameters(self):
        assert (
            self.start_2fa_time.tzinfo is not None
        ), "start_2fa_time must be timezone-aware"
        assert (
            self.end_2fa_time.tzinfo is not None
        ), "end_2fa_time must be timezone-aware"
        assert (
            self.start_2fa_time < self.end_2fa_time
        ), "start_2fa_time must be before end_2fa_time"
        return self


class FetchSlackTwoFARequest(BaseModel):
    slack_workspace_domain: str
    channel_name: str
    sender_name: str
    start_2fa_time: datetime
    end_2fa_time: datetime

    @model_validator(mode="after")
    def validate_time_parameters(self):
        assert (
            self.start_2fa_time.tzinfo is not None
        ), "start_2fa_time must be timezone-aware"
        assert (
            self.end_2fa_time.tzinfo is not None
        ), "end_2fa_time must be timezone-aware"
        assert (
            self.start_2fa_time < self.end_2fa_time
        ), "start_2fa_time must be before end_2fa_time"
        return self


class FetchTwoFAResponse(BaseModel):
    message_id: str
    message_text: str
    otp: str
