from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    title: str
    summary: str
    url: str
    source: str  # "newsapi" | "guardian" | "reddit"
    published_at: Optional[str] = None
