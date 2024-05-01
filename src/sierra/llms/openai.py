import logging
from typing import Optional

from hyfi.composer import BaseModel, Field, SecretStr
from hyfi.env import Env
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class ChatConfig(BaseModel):
    model: str = "gpt-4-turbo"
    temperature: float = 0.0


class ChatEnv(Env):
    OPENAI_API_KEY: Optional[SecretStr] = Field(exclude=True, default="")


class ChatOpenAIModel(BaseModel):
    _config_group_: str = "/llm"
    _config_name_: str = "openai"

    api_key: Optional[str] = None
    model_config: ChatConfig = ChatConfig()
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

        if isinstance(self.model_config, dict):
            self.model_config = ChatConfig(**self.model_config)
            logger.info("ChatConfig is set successfully. %s", self.model_config)
        logger.info("OpenAI API Key is set successfully.")
        self._engine_ = ChatOpenAI(
            api_key=api_key,
            model=self.model_config.model,
            temperature=self.model_config.temperature,
            model_kwargs={"seed": self.seed},
        )
        logger.info("ChatOpenAI is initialized.")
