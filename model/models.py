from pydantic import BaseModel, Field
from typing import List, Annotated


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