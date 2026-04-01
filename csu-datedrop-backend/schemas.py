from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuizSubmit(BaseModel):
    """问卷提交体：硬性字段可顶层传入；若前端整包发送 quiz 对象，会在校验前拆出 raw_quiz_data。"""

    model_config = ConfigDict(extra="forbid")

    gender: Optional[str] = None
    campus: Optional[str] = None
    crossCampus: Optional[str] = None
    sexuality: Optional[str] = None
    raw_quiz_data: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def split_hard_filters(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if data.get("raw_quiz_data") is not None:
            return data
        hard_keys = {"gender", "campus", "crossCampus", "sexuality"}
        out = {k: data[k] for k in hard_keys if k in data}
        out["raw_quiz_data"] = {k: v for k, v in data.items() if k not in hard_keys}
        return out


# --- Auth ---


class RegisterRequest(BaseModel):
    email: str = Field(..., description="完整邮箱或学号（将自动补全 @csu.edu.cn）")
    password: str = Field(..., min_length=6)
    name: str
    campus: str
    grade: str
    major: str


class LoginRequest(BaseModel):
    email: str
    password: str


# --- User ---


class WechatUpdateRequest(BaseModel):
    wechat: str = ""


class ShootRequest(BaseModel):
    target_email: str
    message: str = ""


class PausedRequest(BaseModel):
    paused: bool


class RunMatchBody(BaseModel):
    week_id: Optional[int] = None
