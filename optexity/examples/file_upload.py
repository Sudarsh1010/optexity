from optexity.schema.actions.assertion_action import AssertionAction, LLMAssertion
from optexity.schema.actions.interaction_action import (
    ClickElementAction,
    InteractionAction,
    SelectOptionAction,
    UploadFileAction,
)
from optexity.schema.automation import ActionNode, Automation, Parameters

description = "File Upload Example"
endpoint_name = "file_upload"
automation = Automation(
    url="https://www.azurespeed.com/Azure/UploadLargeFile",
    parameters=Parameters(
        input_parameters={
            "target_region_option": ["test_region"],
            "file_path": ["/path/to/test/file.txt"],
        },
        generated_parameters={},
        secure_parameters={},
    ),
    nodes=[
        ActionNode(
            interaction_action=InteractionAction(
                select_option=SelectOptionAction(
                    command="""get_by_label("Target region")""",
                    select_values=["{target_region_option[0]}"],
                    prompt_instructions="Select an option from the field labeled 'Target region' with the value from the 'target_region_option' variable.",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                upload_file=UploadFileAction(
                    command="""get_by_role("button", name="Test file")""",
                    file_path="{file_path[0]}",
                    prompt_instructions="Click on the 'Test file' button.",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_role("button", name="Start test")""",
                    prompt_instructions="Click the 'Start test' button",
                )
            )
        ),
        ActionNode(
            assertion_action=AssertionAction(
                llm=LLMAssertion(
                    extraction_instructions="Check if the file upload was successful",
                )
            ),
            before_sleep_time=10.0,
        ),
    ],
)
