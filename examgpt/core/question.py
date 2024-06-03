from enum import Enum

from langchain_core.pydantic_v1 import BaseModel, Field


class Scenario(Enum):
    LONGFORM = "long_form"
    MULTIPLECHOICE = "multiple_choice"
    ANSWER = "answer"
    CONTEXTCHECK = "context_check"


class AnswerOption(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class LongForm(BaseModel):
    question: str = Field(description="An exam question with a longform answer")
    answer: str = Field(description="A longform answer to an exam question")

    # TODO: add validators

    def __str__(self) -> str:
        return f"Question: {self.question}\nAnswer: {self.answer}"


class ComplexMultipleChoice(BaseModel):
    question: str = Field(description="An exam question with a multiple choice answers")
    answer: AnswerOption = Field(description="Answer to a multiple choice question")
    choices: dict[AnswerOption, str] = Field(
        description="A dict of 4 choices for an exam question, out of which one is corrrect",
    )

    # TODO: add validators

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Question: {self.question}",
                "Choices:",
                *[f"{key.value}: {value}" for key, value in self.choices.items()],
                f"Answer: {self.answer.value}",
            ]
        )


# TODO: Pick between ComplexMultipleChoice and MultipleChoice
class MultipleChoice(BaseModel):
    question: str = Field(description="An exam question with a multiple choice answers")
    answer: str = Field(
        description="""
            Answer key to a multiple choice question.
            Possible values are A, B, C, D"""
    )
    choices: dict[str, str] = Field(
        description="""
            A dict of key and value for 4 choices for an exam question, out of which one is corrrect. 
            The possible key values are A, B, C, D and value contains the possible answer""",
    )

    # TODO: add validators

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Question: {self.question}",
                "Choices:",
                *[f"{key}: {value}" for key, value in self.choices.items()],
                f"Answer: {self.answer}",
            ]
        )


class LongformEnhanced(LongForm):
    chunk_id: str


class MultipleChoiceEnhanced(BaseModel):
    chunk_id: str
