from optexity.schema.actions.extraction_action import ExtractionAction, LLMExtraction
from optexity.schema.actions.interaction_action import (
    ClickElementAction,
    GoBackAction,
    InputTextAction,
    InteractionAction,
    SelectOptionAction,
)
from optexity.schema.automation import ActionNode, Automation, ForLoopNode

pshpgeorgia_login_test = Automation(
    name="PSHP Georgia Login Test",
    description="Login to PSHP Georgia",
    nodes=[
        ActionNode(
            interaction_action=InteractionAction(
                input_text=InputTextAction(
                    command="""get_by_test_id("text-field")""",
                    input_text="{username[0]}",
                    prompt_instructions="Enter the email in the text field",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_role("button", name="Continue")""",
                    prompt_instructions="Click the Continue button",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                input_text=InputTextAction(
                    command="""get_by_role("textbox", name="Password")""",
                    input_text="{password[0]}",
                    prompt_instructions="Enter the password",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_role("button", name="Login")""",
                    prompt_instructions="Click the Login button",
                )
            )
        ),
    ],
)


pshpgeorgia_medicaid_test = Automation(
    name="PSHP Georgia Medicaid Test",
    description="Get the PSHP Georgia Medicaid application",
    nodes=[
        ActionNode(
            interaction_action=InteractionAction(
                select_option=SelectOptionAction(
                    command="""get_by_label("Plan Type")""",
                    select_values=["{plan_type[0]}"],
                    prompt_instructions="Select the Plan Type 8774789",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_role("button", name="GO")""",
                    prompt_instructions="Click the GO button",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                input_text=InputTextAction(
                    command="""get_by_test_id("MemberIDOrLastName")""",
                    input_text="{member_id[0]}",
                    prompt_instructions="Enter the Member ID or Last Name",
                )
            ),
            end_sleep_time=0,
        ),
        ActionNode(
            interaction_action=InteractionAction(
                input_text=InputTextAction(
                    command="""locator("#tDatePicker")""",
                    input_text="{dob[0]}",
                    prompt_instructions="Enter the Date of Birth",
                )
            ),
            end_sleep_time=0,
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_role("combobox", name="Select Action Type Select")""",
                    prompt_instructions="Click the Select Action Type Select combobox",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_test_id("ActionType-option-0")""",
                    prompt_instructions="Click the View eligibility & patient info option",
                )
            )
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_test_id("submitBtn")""",
                    prompt_instructions="Click the Submit button",
                )
            ),
            end_sleep_time=5,
        ),
        ActionNode(
            interaction_action=InteractionAction(
                click_element=ClickElementAction(
                    command="""get_by_label("Eligibility", exact=True).get_by_role("link", name="Authorizations")""",
                    prompt_instructions="Click the Authorizations link",
                )
            )
        ),
        ActionNode(
            extraction_action=ExtractionAction(
                llm=LLMExtraction(
                    source=["axtree"],
                    extraction_format={
                        "authorization_numbers": "list[str]",
                    },
                    extraction_instructions="Extract the authorization number",
                    output_variable_names=["authorization_numbers"],
                )
            ),
            end_sleep_time=0,
        ),
        ForLoopNode(
            variable_name="authorization_numbers",
            nodes=[
                ActionNode(
                    interaction_action=InteractionAction(
                        click_element=ClickElementAction(
                            command="""get_by_role("link", name="{authorization_numbers[index]}")""",
                            prompt_instructions="Click the Authorizations link for the authorization number {authorization_numbers[index]}",
                        )
                    )
                ),
                ActionNode(
                    interaction_action=InteractionAction(go_back=GoBackAction())
                ),
            ],
        ),
    ],
)
