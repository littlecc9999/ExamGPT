from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from loguru import logger

from examgpt.core.exceptions import (
    NoScenariosProvided,
    NotEnoughInformationInContext,
    UnSupportedScenario,
)
from examgpt.core.question import (
    LongForm,
    LongformEnhanced,
    MultipleChoice,
    MultipleChoiceEnhanced,
    QACollection,
    Scenario,
)
from examgpt.utils.checkpoint import CheckpointService

if TYPE_CHECKING:
    from examgpt.ai.aimodel import AIModel
    from examgpt.sources.chunkers.base import Chunker, TextChunk


class SourceType(Enum):
    PDF = "PDF"
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"


@dataclass
class Source(ABC):
    location: str
    chunker: Chunker
    type: SourceType
    chunks: list[TextChunk] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    full_text: str | None = None

    def __post_init__(self):
        file = Path(self.location).resolve()
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        self.location = str(file)

    @abstractmethod
    def chunk(self) -> list[TextChunk]: ...

    @abstractmethod
    def create_text(self) -> str: ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...

    @staticmethod
    @abstractmethod
    def from_dict(source_dict: dict[str, Any]) -> Source: ...

    def update_location(self, new_location: str) -> None:
        self.location = new_location

    def limit_chunks(self, n: int = 5) -> None:
        self.chunks = self.chunks[:n]

    def get_qa_collection(
        self,
        exam_id: str,
        exam_name: str,
        model: AIModel,
        scenarios: list[Scenario] = [Scenario.LONGFORM, Scenario.MULTIPLECHOICE],
    ) -> QACollection | None:
        if not scenarios:
            raise NoScenariosProvided()
        if not self.chunks:
            logger.warning("Chunk the document before asking to generate Q&A")
            return None

        data = CheckpointService.load_checkpoint()
        args = {} if data is None else data
        args["exam_id"] = exam_id
        args["source_id"] = self.id

        for scenario in scenarios:
            if scenario == Scenario.LONGFORM:
                longform_qas: list[LongformEnhanced] = []

                completed_chunks: list[str] = []
                if "long_form_qa" in args:
                    longform_qas = args["long_form_qa"]
                    completed_chunks = [qa.chunk_id for qa in longform_qas]

                for chunk in self.chunks:
                    if chunk.id in completed_chunks:
                        continue

                    logger.info(f"Generating long form QA for chunk: {chunk.id}")
                    try:
                        qa = model.generate_longform_qa(chunk, exam_name)
                        qae = LongformEnhanced(**qa.dict(), chunk_id=chunk.id)
                    except NotEnoughInformationInContext as e:
                        logger.warning(e.message)
                        qae = LongformEnhanced(
                            question="", answer="", chunk_id=chunk.id
                        )

                    longform_qas.append(qae)
                    args["long_form_qa"] = longform_qas
                    CheckpointService.save_checkpoint(args)

            elif scenario == Scenario.MULTIPLECHOICE:
                multiplechoice_qas: list[MultipleChoiceEnhanced] = []

                completed_chunks: list[str] = []
                if "multiple_choice_qa" in args:
                    multiplechoice_qas = args["multiple_choice_qa"]
                    completed_chunks = [qa.chunk_id for qa in multiplechoice_qas]

                for chunk in self.chunks:
                    if chunk.id in completed_chunks:
                        continue

                    logger.info(f"Generating multiple choice QA for chunk: {chunk.id}")
                    try:
                        qa = model.generate_multiplechoice_qa(chunk, exam_name)
                        qae = MultipleChoiceEnhanced(**qa.dict(), chunk_id=chunk.id)
                    except NotEnoughInformationInContext as e:
                        logger.warning(e.message)
                        qae = MultipleChoiceEnhanced(
                            question="", answer="", choices={}, chunk_id=chunk.id
                        )

                    multiplechoice_qas.append(qae)
                    args["multiple_choice_qa"] = multiplechoice_qas
                    CheckpointService.save_checkpoint(args)

            else:
                raise UnSupportedScenario(str(scenario))

        return QACollection(**args)

    def test_checkpoint_test(
        self,
        exam_id: str,
        exam_name: str,
        model: AIModel,
        scenarios: list[Scenario] = [Scenario.LONGFORM, Scenario.MULTIPLECHOICE],
    ) -> QACollection | None:
        if not scenarios:
            raise NoScenariosProvided()
        if not self.chunks:
            logger.warning("Chunk the document before asking to generate Q&A")
            return None

        data = CheckpointService.load_checkpoint()
        args = {} if data is None else data
        args["exam_id"] = exam_id
        args["source_id"] = self.id

        for scenario in scenarios:
            if scenario == Scenario.LONGFORM:
                longform_qas: list[LongformEnhanced] = []

                completed_chunks: list[str] = []
                if "long_form_qa" in args:
                    longform_qas = args["long_form_qa"]
                    completed_chunks = [qa.chunk_id for qa in longform_qas]

                for i, chunk in enumerate(self.chunks):
                    if chunk.id in completed_chunks:
                        logger.info(
                            f"Iteration: {i} for long form skipped. chunk: {chunk.id}"
                        )
                        continue

                    logger.info(
                        f"Generating long form QA for Iteration: {i} chunk: {chunk.id}"
                    )
                    try:
                        time.sleep(0.5)
                        qa = LongForm(question=f"{i}", answer=f"{i}")
                        qae = LongformEnhanced(**qa.dict(), chunk_id=chunk.id)
                    except NotEnoughInformationInContext as e:
                        logger.warning(e.message)
                        qae = LongformEnhanced(
                            question="", answer="", chunk_id=chunk.id
                        )

                    longform_qas.append(qae)
                    args["long_form_qa"] = longform_qas
                    CheckpointService.save_checkpoint(args)

            elif scenario == Scenario.MULTIPLECHOICE:
                multiplechoice_qas: list[MultipleChoiceEnhanced] = []

                completed_chunks: list[str] = []
                if "multiple_choice_qa" in args:
                    multiplechoice_qas = args["multiple_choice_qa"]
                    completed_chunks = [qa.chunk_id for qa in multiplechoice_qas]

                for i, chunk in enumerate(self.chunks):
                    if chunk.id in completed_chunks:
                        logger.info(
                            f"Iteration: {i} multiple choice skipped. chunk: {chunk.id}"
                        )
                        continue

                    logger.info(
                        f"Generating multiple choice QA for Iteration {i} chunk: {chunk.id}"
                    )
                    try:
                        time.sleep(0.5)
                        qa = MultipleChoice(question=f"{i}", answer=f"{i}", choices={})
                        qae = MultipleChoiceEnhanced(**qa.dict(), chunk_id=chunk.id)
                    except NotEnoughInformationInContext as e:
                        logger.warning(e.message)
                        qae = MultipleChoiceEnhanced(
                            question="", answer="", choices={}, chunk_id=chunk.id
                        )

                    multiplechoice_qas.append(qae)
                    args["multiple_choice_qa"] = multiplechoice_qas
                    CheckpointService.save_checkpoint(args)

            else:
                raise UnSupportedScenario(str(scenario))

        return QACollection(**args)
