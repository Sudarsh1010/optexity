from typing import Literal

from pydantic import BaseModel, model_validator


class Locator(BaseModel):
    regex_options: list[str] | None = None
    locator_class: str
    first_arg: str | int | None = None
    options: dict | None = None


class DialogAction(BaseModel):
    action: Literal["accept", "reject"]
    prompt_instructions: str


class BaseAction(BaseModel):
    index: int | None = None
    xpath: str | None = None
    command: str | None = None
    prompt_instructions: str

    @model_validator(mode="after")
    def validate_one_extraction(cls, model: "BaseAction"):
        """Ensure exactly one of the extraction types is set and matches the type."""
        provided = {
            "xpath": model.xpath,
            "command": model.command,
        }
        non_null = [k for k, v in provided.items() if v is not None]

        if len(non_null) != 1:
            raise ValueError(
                "Exactly one of llm, networkcall, or python must be provided"
            )

        return model


class CheckAction(BaseAction):
    pass


class SelectOptionAction(BaseAction):
    select_values: list[str]
    download_filename: str | None = None


class ClickElementAction(BaseAction):
    double_click: bool = False
    download_filename: str | None = None


class InputTextAction(BaseAction):
    input_text: str | None = None
    is_slider: bool = False
    fill_or_type: Literal["fill", "type"] = "fill"


class DownloadUrlAsPdfAction(BaseModel):
    # Used when the current page is a PDF and we want to download it
    pass


class ScrollAction(BaseModel):
    down: bool  # True to scroll down, False to scroll up


class UploadFileAction(BaseAction):
    file_path: str


class GoToUrlAction(BaseModel):
    url: str
    new_tab: bool = False  # True to open in new tab, False to navigate in current tab


class GoBackAction(BaseModel):
    pass


class SwitchTabAction(BaseModel):
    tab_index: int


class CloseCurrentTabAction(BaseModel):
    pass


class CloseAllButLastTabAction(BaseModel):
    pass


class InteractionAction(BaseModel):
    click_element: ClickElementAction | None = None
    input_text: InputTextAction | None = None
    select_option: SelectOptionAction | None = None
    check: CheckAction | None = None
    download_url_as_pdf: DownloadUrlAsPdfAction | None = None
    scroll: ScrollAction | None = None
    upload_file: UploadFileAction | None = None
    go_to_url: GoToUrlAction | None = None
    go_back: GoBackAction | None = None
    switch_tab: SwitchTabAction | None = None
    close_current_tab: CloseCurrentTabAction | None = None
    close_all_but_last_tab: CloseAllButLastTabAction | None = None

    @model_validator(mode="after")
    def validate_one_interaction(cls, model: "InteractionAction"):
        """Ensure exactly one of the interaction types is set and matches the type."""
        provided = {
            "click_element": model.click_element,
            "input_text": model.input_text,
            "select_option": model.select_option,
            "check": model.check,
            "download_url_as_pdf": model.download_url_as_pdf,
            "scroll": model.scroll,
            "upload_file": model.upload_file,
            "go_to_url": model.go_to_url,
            "go_back": model.go_back,
            "switch_tab": model.switch_tab,
            "close_current_tab": model.close_current_tab,
            "close_all_but_last_tab": model.close_all_but_last_tab,
        }
        non_null = [k for k, v in provided.items() if v is not None]

        if len(non_null) != 1:
            raise ValueError(
                "Exactly one of click_element, input_text, select_option, check, download_url_as_pdf, scroll, upload_file, go_to_url, go_back, switch_tab, close_current_tab, or close_all_but_last_tab must be provided"
            )

        return model
