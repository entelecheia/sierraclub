import logging
from typing import Optional

from hyfi.composer import BaseModel, Field
from hyfi.env import Env
from langchain_community.chat_models import ChatOllama

logger = logging.getLogger(__name__)


class ChatConfig(BaseModel):
    model: str = "llama3"
    temperature: float = 0.0


class ChatEnv(Env):
    OLLAMA_BASE_URL: Optional[str] = Field(
        exclude=True, default="http://localhost:11434"
    )


class ChatOllamaModel(BaseModel):
    _config_group_: str = "/llm"
    _config_name_: str = "ollama"

    api_key: Optional[str] = None
    model_config: ChatConfig = ChatConfig()
    seed: Optional[int] = None
    env: ChatEnv = ChatEnv()

    _engine_: Optional[ChatOllama] = None

    @property
    def engine(self):
        if self._engine_ is None:
            self.initialize()
        return self._engine_

    def initialize(self):
        if isinstance(self.model_config, dict):
            self.model_config = ChatConfig(**self.model_config)
            logger.info("ChatConfig is set successfully. %s", self.model_config)
        self._engine_ = ChatOllama(
            base_url=self.env.OLLAMA_BASE_URL,
            model=self.model_config.model,
            temperature=self.model_config.temperature,
            model_kwargs={"seed": self.seed},
        )
        logger.info("ChatOllama is initialized.")
