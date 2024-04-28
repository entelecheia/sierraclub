import logging
from typing import Any, Dict, Optional

from hyfi.composer import BaseModel, Field, SecretStr
from hyfi.env import Env
from langchain.chat_models import ChatOpenAI

logger = logging.getLogger(__name__)


class ChatConfig(BaseModel):
    model: str
    temperature: float
    # messages: List[ChatMessage]


class ChatResponse(BaseModel):
    content: str
    usage: Dict[str, Any] = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }


class ChatEnv(Env):
    OPENAI_API_KEY: Optional[SecretStr] = Field(exclude=True, default="")


class OpenAIChat(BaseModel):
    _config_group_: str = "/llm"
    _config_name_: str = "openai"

    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    rate_limit_per_minute: int = 3500
    temperature: float = 0.0
    seed: Optional[int] = None
    env: ChatEnv = ChatEnv()

    _engine_: Optional[ChatOpenAI] = None

    @property
    def engine(self):
        if self._engine_ is None:
            self.initialize()
        return self._engine_

    def initialize(self, api_key: Optional[str] = None):
        api_key = api_key or self.api_key
        if not api_key and self.env.OPENAI_API_KEY:
            api_key = self.env.OPENAI_API_KEY.get_secret_value()
        if not api_key:
            raise ValueError("OpenAI API Key is required.")

        logger.info("OpenAI API Key is set successfully.")
        self._engine_ = ChatOpenAI(
            model=self.model,
            api_key=api_key,
            temperature=self.temperature,
            model_kwargs={"seed": self.seed},
        )
        logger.info("ChatOpenAI is initialized.")

    # def build_config(self, message: ChatMessage) -> Dict[str, Any]:
    #     return ChatConfig(
    #         model=self.model,
    #         temperature=self.temperature,
    #         messages=[message],
    #     ).model_dump()

    # def request(self, message: ChatMessage) -> ChatResponse:
    #     delay = 60.0 / self.rate_limit_per_minute
    #     return call_api(
    #         self.engine,
    #         self.build_config(message),
    #         delay_in_seconds=delay,
    #     )


# @tenacity.retry(
#     wait=tenacity.wait_exponential(multiplier=1, min=4, max=60 * 5),
#     retry=tenacity.retry_if_exception_type(
#         (
#             RateLimitError,
#             APIConnectionError,
#             APIError,
#             InternalServerError,
#         )
#     ),
#     stop=tenacity.stop_after_attempt(20),
#     after=tenacity.after_log(logger, logging.INFO),
#     before_sleep=tenacity.before_sleep_log(logger, logging.INFO),
# )
# def request_api(engine, args, delay_in_seconds: float = 1):
#     time.sleep(delay_in_seconds)
#     return engine.completions.create(**args)


# def call_api(engine, args, delay_in_seconds: float = 1) -> ChatResponse:
#     time.sleep(delay_in_seconds)
#     try:
#         response = request_api(engine, args, delay_in_seconds=delay_in_seconds)
#         message = response["choices"][0]["message"]
#         content = message["content"].strip().strip("\n")
#         usage = response["usage"]
#         return ChatResponse(content=content, usage=usage)
#     except BadRequestError as e:
#         logger.error(e)
#         return ChatResponse(content=e.user_message)
#     except Exception as e:
#         logger.error(e)
#         return ChatResponse(content=str(e))
