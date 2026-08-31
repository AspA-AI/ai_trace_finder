from pydantic import BaseModel, Field


class PersonClues(BaseModel):
    """Sparse user-provided clues; this model makes no identity conclusion."""

    name: str | None = None
    usernames: list[str] = Field(default_factory=list)
    occupation: str | None = None
    employers: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    websites: list[str] = Field(default_factory=list)
    github_handle: str | None = None
    additional_clues: list[str] = Field(default_factory=list)
