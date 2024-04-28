# This file is used to extract data from the content using the langchain library
from langchain.chains import create_extraction_chain_pydantic
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")


def extract(content: str, **kwargs):

    if schema := kwargs.get("schema", None):
        response = create_extraction_chain_pydantic(
            pydantic_schema=schema, llm=llm
        ).run(content)
        return [item.dict() for item in response]
