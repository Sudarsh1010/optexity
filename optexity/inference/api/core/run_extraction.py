import logging

from optexity.inference.api.infra.browser import Browser
from optexity.inference.api.models import GeminiModels, get_llm_model
from optexity.schema.actions.extraction_action import ExtractionAction, LLMExtraction
from optexity.schema.memory import Memory

logger = logging.getLogger(__name__)

llm_model = get_llm_model(GeminiModels.GEMINI_2_5_FLASH, True)


async def run_extraction_action(
    extraction_action: ExtractionAction, memory: Memory, browser: Browser
):
    logger.debug(
        f"---------Running extraction action {extraction_action.model_dump_json()}---------"
    )

    if extraction_action.llm:
        await handle_llm_extraction(extraction_action.llm, memory, browser)


async def handle_llm_extraction(
    llm_extraction: LLMExtraction, memory: Memory, browser: Browser
):
    if "axtree" in llm_extraction.source:
        axtree = await browser.get_axtree()
    if "screenshot" in llm_extraction.source:
        screenshot = None
        # screenshot = await browser.get_screenshot()

    prompt = "Extract the following from the axtree: " + axtree
    response, token_usage = llm_model.get_model_response_with_structured_output(
        prompt=prompt,
        response_schema=llm_extraction.build_model(),
        screenshot=screenshot,
    )

    memory.token_usage += token_usage
    memory.variables.output_data.append(response.model_dump())

    for output_variable_name in llm_extraction.output_variable_names:
        memory.variables.generated_variables[output_variable_name] = response[
            output_variable_name
        ]
