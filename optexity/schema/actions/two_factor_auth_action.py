from typing import Literal

from pydantic import BaseModel


class BaseTwoFactorAuthAction(BaseModel):
    integration_id: str


class EmailTwoFactorAuthAction(BaseTwoFactorAuthAction):
    type: Literal["email_two_factor_auth"] = "email_two_factor_auth"
    email_address: str


class SlackTwoFactorAuthAction(BaseTwoFactorAuthAction):
    type: Literal["slack_two_factor_auth"] = "slack_two_factor_auth"
    channel_id: str


class TwoFactorAuthAction(BaseModel):
    action: EmailTwoFactorAuthAction | SlackTwoFactorAuthAction
    output_variable_name: str
    max_wait_time: float = 300.0
