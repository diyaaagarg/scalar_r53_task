from typing import Literal

from pydantic import BaseModel, Field


class BindImportRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1_000_000)
    format: Literal["BIND"] = "BIND"


class ImportResult(BaseModel):
    created_count: int
