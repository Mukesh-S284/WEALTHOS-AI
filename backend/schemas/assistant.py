"""Assistant Chat Pydantic schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AssistantChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)


class ToolCallRecord(BaseModel):
    name: str
    arguments: Dict[str, Any]


class CitationItem(BaseModel):
    title: str
    publisher: str
    date: Optional[str] = None
    excerpt: str


class AssistantChatResponse(BaseModel):
    session_id: str
    role: str = "assistant"
    content: str
    tool_calls: List[Dict[str, Any]] = []
    tool_results: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    model: str
    provider: str


class AssistantMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AssistantSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[AssistantMessageResponse] = []

    class Config:
        from_attributes = True
