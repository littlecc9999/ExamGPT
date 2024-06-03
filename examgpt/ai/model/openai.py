from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI

from examgpt.ai.base import ModelConfig
from examgpt.ai.constants import ModelFamily, ModelName


@dataclass
class OpenAIConfig(ModelConfig):
    family: ModelFamily = field(default=ModelFamily.OPENAI)
    name: ModelName = field(default=ModelName.GPT3_5_TURBO)
    cost_ppm_token: int = 50
    chunk_size: int = 2500


class OpenAIProvider:
    def __init__(self):
        self.model_config = OpenAIConfig()
        self.chat = ChatOpenAI(model=str(self.model_config.name.value))

    def get_chat_model(self) -> ChatOpenAI:
        return self.chat

    def get_model_name(self) -> ModelName:
        return ModelName.DEFAULT
