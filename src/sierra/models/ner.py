from typing import List, Optional

from hyfi.composer import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel as BaseModelV1
from langchain_core.pydantic_v1 import Field as FieldV1

from sierra.llms import ChatOpenAIModel


class EventEntity(BaseModelV1):
    events: List[str] = FieldV1(description="The events extracted from the text")
    entities: List[str] = FieldV1(description="The entities extracted from the text")


class EventEntityExtractor(BaseModel):
    _config_group_: str = "/llm"
    _config_name_: str = "openai"

    llm_model: ChatOpenAIModel = ChatOpenAIModel()

    _engine_: Optional[ChatOpenAI] = None
    _output_parser_: Optional[PydanticOutputParser] = None
    _prompt_: Optional[ChatPromptTemplate] = None

    def initialize(self):
        self._engine_ = self.llm_model.engine
        self._output_parser_ = self._create_output_parser()
        self._prompt_ = self._create_prompt()

    @property
    def engine(self) -> ChatOpenAI:
        if self._engine_ is None:
            self.initialize()
        return self._engine_

    @property
    def output_parser(self) -> PydanticOutputParser:
        if self._output_parser_ is None:
            self.initialize()
        return self._output_parser_

    @property
    def prompt(self) -> ChatPromptTemplate:
        if self._prompt_ is None:
            self.initialize()
        return self._prompt_

    @property
    def chain(self):
        return self.prompt | self.engine

    def extract_events_entities(self, input_text: str) -> EventEntity:
        return self.chain.invoke({"text": input_text})

    def _create_output_parser(self) -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=EventEntity)

    def _create_prompt(self):
        event_entity_template = """
        Your goal is to understand and parse out the events and entities from the given text.

        {format_instructions}

        text: {text}
        """
        format_instructions = self.output_parser.get_format_instructions()
        return ChatPromptTemplate.from_template(
            template=event_entity_template,
            partial_variables={"format_instructions": format_instructions},
        )


def main():
    extractor = EventEntityExtractor()
    input_text = """Agency’s Shift Places Conservation on Equal Footing with Development
April 18, 2024


Contact
Ian Brickey, 202-675-6270 or ian.brickey@sierraclub.org


WASHINGTON, D.C. – Today, the Biden Administration announced a federal rule that will introduce a new vision for how the Bureau of Land Management’s (BLM) mission addresses the climate and biodiversity crises. The newly announced rule re-balances BLM’s multi-use mandate for managing public lands, which for decades had favored resource extraction over any other use. Currently, oil and gas leasing is allowed on 90 percent of BLM-managed lands. Now, conservation is placed on equal footing with mining, drilling, and other uses, highlighting BLM’s priorities of healthy wildlife habitat, clean water, access to nature, cultural resource protection, and ecosystem resilience.The new rule implements restoration and mitigation leases, which will help restore degraded landscapes and lessen environmental impacts from other uses on public lands. It also introduces the consideration of land health into all BLM decision-making. These changes are likely to help achieve the scientifically identified goal of protecting 30 percent of lands and waters in the U.S. to stave off the worst effects of climate change. In response, Sierra Club Executive Director Ben Jealous released the following statement:“For years, BLM managed public lands for multiple uses – as long as those uses were exploiting these lands for fossil fuels. That ends today. From now on, public lands will be managed for public benefit, not just for the profits of the oil and gas industry.“As the largest manager of public lands in the country, BLM has a critical role in the U.S. strategy for addressing climate change and the extinction crisis. With this new rule, the agency can finally take on that responsibility. “Let’s be clear, this is a new chapter in BLM’s management of public lands, and it shows that the Biden Administration takes the conservation of American lands and waters seriously. This is the kind of bold action required to take on the climate and extinction crises.”

About the Sierra Club
The Sierra Club is America’s largest and most influential grassroots environmental organization, with millions of members and supporters. In addition to protecting every person's right to get outdoors and access the healing power of nature, the Sierra Club works to promote clean energy, safeguard the health of our communities, protect wildlife, and preserve our remaining wild places through grassroots activism, public education, lobbying, and legal action. For more information, visit www.sierraclub.org.


More From This Press Contact

Ian Brickey"""
    print(input_text)
    result = extractor.extract_events_entities(input_text)
    print(result.content)


if __name__ == "__main__":
    main()
