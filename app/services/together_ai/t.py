import os
from typing import TypedDict

import together


class ModelParametersType(TypedDict):
    model_name: str
    max_tokens: int
    temperature: float
    top_k: int
    top_p: float
    repetition_penalty: float
    stop_word: str


class TogetherAIUtils:
    # "Phind/Phind-CodeLlama-34B-Python-v1"
    # "WizardLM/WizardCoder-Python-34B-V1.0"
    DEFAULT_MODEL_NAME = "Open-Orca/Mistral-7B-OpenOrca"
    DEFAULT_MAX_TOKENS = 250
    DEFAULT_TEMPERATURE = 2.0
    DEFAULT_TOP_K = 50
    DEFAULT_TOP_P = 0.7
    DEFAULT_REPETITION_PENALTY = 1.0
    DEFAULT_STOP_WORD = "### User Message"

    def __init__(self, model_parameters: ModelParametersType = None):
        self.api_key = os.environ.get('TOGETHER_AI_KEY', None)
        self.history_pairs = []
        self.model_parameters: ModelParametersType = {} if model_parameters is None else model_parameters

    def get_model(self) -> str:
        return self.model_parameters["model_name"]

    def make_request(self, prompt: str) -> str:
        output = together.Complete.create(
            prompt=prompt,
            model=self.get_model(),
            max_tokens=self.model_parameters.get("max_tokens", self.DEFAULT_MAX_TOKENS),
            temperature=self.model_parameters.get("temperature", self.DEFAULT_TEMPERATURE),
            top_k=self.model_parameters.get("top_k", self.DEFAULT_TOP_K),
            top_p=self.model_parameters.get("top_p", self.DEFAULT_TOP_P),
            repetition_penalty=self.model_parameters.get("repetition_penalty", self.DEFAULT_REPETITION_PENALTY),
            stop=[self.model_parameters.get("stop_word", self.DEFAULT_STOP_WORD)]
            )
        # return generated text
        return output['output']['choices'][0]["text"]
