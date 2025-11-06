import logging

from optexity.inference.api.infra.browser import Browser
from optexity.schema.actions.interaction_action import (
    ClickElementAction,
    InputTextAction,
    InteractionAction,
)
from optexity.schema.memory import Memory

logger = logging.getLogger(__name__)


def get_index_from_prompt(prompt: str, axtree: str) -> int | None:
    raise NotImplementedError("Not implemented")


async def run_interaction_action(
    interaction_action: InteractionAction, memory: Memory, browser: Browser
):
    logger.debug(
        f"---------Running interaction action {interaction_action.model_dump_json()}---------"
    )

    if interaction_action.click_element:
        await handle_click_element(interaction_action.click_element, memory, browser)

    elif interaction_action.input_text:
        await handle_input_text(interaction_action.input_text, memory, browser)
    elif interaction_action.select_option:
        pass


async def handle_click_element(
    click_element_action: ClickElementAction, memory: Memory, browser: Browser
):
    if click_element_action.command:
        try:
            locator = await browser.get_locator_from_command(
                click_element_action.command
            )
            if click_element_action.double_click:
                await locator.dblclick()
            else:
                await locator.click()

            # if download_filename:
            #     await self.expect_download(download_filename)

            return
        except Exception as e:
            logger.debug(f"Error in click_element_locator: {e}")
            logger.debug("Falling back to index locator")

    if click_element_action.prompt_instructions:
        memory.automation_state.try_index += 1
        try:
            axtree = await browser.get_axtree()
            memory.browser_states[-1].axtree = axtree
            index = get_index_from_prompt(
                click_element_action.prompt_instructions, axtree
            )
            await browser.click_index(index)
            return
        except Exception as e:
            logger.error(f"Error in get_index_from_prompt: {e}")
            logger.debug("Falling back to index locator")


async def handle_input_text(
    input_text_action: InputTextAction, memory: Memory, browser: Browser
):
    if input_text_action.command:
        try:
            locator = await browser.get_locator_from_command(input_text_action.command)

            if input_text_action.fill_or_type == "fill":
                await locator.fill(input_text_action.input_text)
            else:
                await locator.type(input_text_action.input_text, delay=100)

            return
        except Exception as e:
            logger.debug(f"Error in click_element_locator: {e}")
            logger.debug("Falling back to index locator")

    if input_text_action.prompt_instructions:
        memory.automation_state.try_index += 1
        try:
            axtree = await browser.get_axtree()
            memory.browser_states[-1].axtree = axtree
            index = get_index_from_prompt(input_text_action.prompt_instructions, axtree)
            await browser.input_text_index(index, input_text_action.input_text)
            return
        except Exception as e:
            logger.error(f"Error in get_index_from_prompt: {e}")
            logger.debug("Falling back to index locator")
