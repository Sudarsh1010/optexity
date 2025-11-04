from pydantic import BaseModel, Field


class NetworkRequest(BaseModel):
    url: str = Field(..., description="The URL of the network request")
    method: str = Field(..., description="The method of the network request")
    status: int = Field(..., description="The status of the network request")
    headers: dict = Field(..., description="The headers of the network request")
    body: str = Field(..., description="The body of the network request")


class NetworkError(BaseModel):
    url: str = Field(..., description="The URL of the network error")
    message: str = Field(..., description="The message of the network error")
    stack_trace: str = Field(..., description="The stack trace of the network error")


class NetworkResponse(BaseModel):
    url: str = Field(..., description="The URL of the network response")
    status: int = Field(..., description="The status of the network response")
    headers: dict = Field(..., description="The headers of the network response")
    body: str = Field(..., description="The body of the network response")


class AutomationState(BaseModel):
    step_index: int = Field(..., description="The index of the current step")
    try_index: int = Field(..., description="The index of the current try")


class BrowserState(BaseModel):
    url: str = Field(..., description="The URL of the current page")
    title: str = Field(..., description="The title of the current page")
    screenshot: str = Field(..., description="The screenshot of the current page")
    html: str = Field(..., description="The HTML of the current page")
    axtree: str = Field(..., description="The AXTREE of the current page")


class Variables(BaseModel):
    input_variables: dict = Field(..., description="The input variables")
    output_variables: dict = Field(..., description="The output variables")
    generated_variables: dict = Field(..., description="The generated variables")


class Memory(BaseModel):
    variables: Variables
    automation_state: AutomationState
    browser_states: list[BrowserState]
