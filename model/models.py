from pydantic import BaseModel, Field, RootModel
from typing import List, Annotated
from enum import Enum


class Metadata(BaseModel):
    Summary: Annotated[List[str], Field(default_factory=list, description="Summary of the document")]
    Title: str
    Author: str
    DateCreated: str   
    LastModifiedDate: str
    Publisher: str
    Language: str
    PageCount: int | str  # Can be "Not Available"
    SentimentTone: str

class ChangeFormat(BaseModel):
    Page: str
    Changes: str

class SummaryResponse(RootModel[list[ChangeFormat]]):
    pass
class PromptType(str, Enum):
    DOCUMENT_ANALYSIS = "document_analysis"
    DOCUMENT_COMPARISON = "document_comparison"
    CONTEXTUALIZE_QUESTION = "contextualize_question"
    CONTEXT_QA = "context_qa"