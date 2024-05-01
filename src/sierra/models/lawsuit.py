from typing import List, Optional

from hyfi.composer import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel as BaseModelV1
from langchain_core.pydantic_v1 import Field as FieldV1

from sierra.llms import ChatOpenAIModel


class LawsuitDetails(BaseModelV1):
    has_lawsuit: bool = FieldV1(description="Indicates if the text mentions a lawsuit")
    claimant: List[str] = FieldV1(description="The claimant in the lawsuit")
    defendant: List[str] = FieldV1(description="The defendant in the lawsuit")
    case_summary: str = FieldV1(description="A brief summary of the case")
    case_date: str = FieldV1(description="The date of the lawsuit")
    other_details: Optional[str] = FieldV1(
        description="Any other relevant details about the lawsuit"
    )


class LawsuitExtractor(BaseModel):
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

    def extract_lawsuit_details(self, input_text: str) -> LawsuitDetails:
        return self.chain.invoke({"text": input_text})

    def _create_output_parser(self) -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=LawsuitDetails)

    def _create_prompt(self):
        lawsuit_template = """
        Your goal is to extract the details of a lawsuit from the given text.

        {format_instructions}

        text: {text}
        """
        format_instructions = self.output_parser.get_format_instructions()
        return ChatPromptTemplate.from_template(
            template=lawsuit_template,
            partial_variables={"format_instructions": format_instructions},
        )


def main():
    extractor = LawsuitExtractor()
    input_text = """
Fish and Wildlife Service Illegally Denied Protections to Wolves
April 8, 2024


Contact
Ian Brickey, Sierra Club, (202) 675-6270, ian.brickey@sierraclub.orgCollette Adkins, Center for Biological Diversity, (651) 955-3821, cadkins@biologicaldiversity.orgKate Sarna, The Humane Society of the United States/Humane Society Legislative Fund, (202) 836-1265, ksarna@hslf.org


BOZEMAN, MT — Four conservation and animal protection groups sued the U.S. Fish and Wildlife Service today for denying their petition to protect gray wolves in the northern Rocky Mountains under the Endangered Species Act.“We’re back in court to save the wolves and we’ll win again,” said Collette Adkins, carnivore conservation program director at the Center for Biological Diversity. “The Fish and Wildlife Service is thumbing its nose at the Endangered Species Act and letting wolf-hating states sabotage decades of recovery efforts. It’s heartbreaking and it has to stop.”The petition filed in 2021 by the Center for Biological Diversity, Humane Society of the United States, Humane Society Legislative Fund and Sierra Club sought to restore federal protections to gray wolves in the northern Rockies. The Service denied the petition in February, even though its own scientists predict that rampant wolf killing under state laws could reduce the region’s wolf population from an estimated 2,534 wolves to as few as 667.The agency has ignored warnings from conservation geneticists and other scientists that a sharp decline in population size would imperil the northern Rockies wolves, who are already at long-term risk of extinction. High levels of killing would also hurt wolf recovery elsewhere in United States, like the West Coast and southern Rockies states. Wolf populations in these states rely on wolves traveling from the northern Rockies to increase genetic diversity and ensure a healthy, stable future for the species.“We will not idly stand by while the federal government erases decades of wolf recovery by permitting northern Rockies states to wage war on these animals,” said Margie Robinson, staff attorney for wildlife at the Humane Society of the United States. “Under the Endangered Species Act, the U.S. Fish and Wildlife Service cannot ignore crucial scientific findings. Rather than allow states to cater to trophy hunters, trappers and ranchers, the agency must ensure the preservation of wolves — who are vital to ensuring healthy ecosystems — for generations to come.”Recent changes in Montana state laws allow wolves to be killed using bait and strangulation snares, permit a single hunter to hunt 10 wolves and trap an additional 10, and lengthen the wolf-trapping season. In Idaho, recent changes authorize the state to hire private contractors to kill wolves, allow hunters to purchase an unlimited number of wolf-killing tags and permit hunters to kill wolves by chasing them down with hounds and all-terrain vehicles.Across most of Wyoming wolves are designated as “predatory animals” and can be killed without a license in nearly any manner and at any time. Wyoming hunters have killed several wolves just a few miles from the border with Colorado, where wolves are finally returning to the state through dispersals and historic releases.“The states of Montana, Idaho and Wyoming act like it’s 1880 with the most radical and unethical methods to kill as many wolves as possible in an effort to manage for bare minimum numbers,” said Nick Gevock, northern Rockies field organizer for the Sierra Club. “This kind of management is disgraceful, it’s unnecessary and it sets back wolf conservation decades, and the American people are not going to stand by and allow it to happen.”“While wolves in the northern Rockies remain unprotected, states continue to facilitate the unabated slaughter of this iconic species,” said Gillian Lyons, director of regulatory affairs at the Humane Society Legislative Fund. “The U.S. Fish and Wildlife Service is required to take action when a species is at risk of extinction — and wolves are no exception. Our lawsuit today lets the agency know that we will hold them accountable to their statutory duty to protect species like wolves from extinction.”The conservation groups’ lawsuit seeks a court order requiring the Service to use current science and to reevaluate whether gray wolves in the northern Rocky Mountains warrant Endangered Species Act protection.Today’s lawsuit was filed in the U.S. District Court for the District of Montana.BackgroundWolves in Idaho, Montana, eastern Washington, eastern Oregon and northern Utah lost federal protections through a congressional legislative rider in 2011. Following a court battle, wolves in Wyoming also lost federal protection in 2012. Since losing Endangered Species Act protection, wolves in the northern Rockies have suffered widespread persecution under state law.In August 2022, the groups were forced to sue the Service for failing to make a final decision on the petition to protect gray wolves in the northern Rocky Mountains. The agency’s denial of the groups’ petition was announced in February 2024.In early February 2024, the agency also announced that that it will develop — for the first time — a national recovery plan under the Endangered Species Act for gray wolves in the lower 48 states. That commitment stems from a successful lawsuit by the Center for Biological Diversity. The agency will exclude wolves in the northern Rockies from that planning effort unless they regain their federal protections.

About the Sierra Club
The Sierra Club is America’s largest and most influential grassroots environmental organization, with millions of members and supporters. In addition to protecting every person's right to get outdoors and access the healing power of nature, the Sierra Club works to promote clean energy, safeguard the health of our communities, protect wildlife, and preserve our remaining wild places through grassroots activism, public education, lobbying, and legal action. For more information, visit www.sierraclub.org.


More From This Press Contact

Ian Brickey
"""
    print(input_text)
    result = extractor.extract_lawsuit_details(input_text)
    print(result.content)


if __name__ == "__main__":
    main()
