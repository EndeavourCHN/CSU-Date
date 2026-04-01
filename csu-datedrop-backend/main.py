import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import bcrypt
from jose import JWTError, jwt
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Crush, Match, Profile, User
from schemas import (
    LoginRequest,
    PausedRequest,
    QuizSubmit,
    RegisterRequest,
    ShootRequest,
    WechatUpdateRequest,
)

# --- Security ---

SECRET_KEY = os.getenv("CSU_DATE_SECRET", "dev-csu-date-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer(auto_error=False)

app = FastAPI(title="CSU Date API")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Helpers ---


def normalize_csu_email(raw: str) -> str:
    s = raw.strip().lower()
    if "@" not in s:
        s = f"{s}@csu.edu.cn"
    if not s.endswith("@csu.edu.cn"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须使用 @csu.edu.cn 邮箱",
        )
    return s


def _password_bytes(plain: str) -> bytes:
    """bcrypt 仅使用前 72 字节。"""
    return plain.encode("utf-8")[:72]


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(_password_bytes(plain), hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_password_bytes(plain), bcrypt.gensalt()).decode("ascii")


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> int:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = data.get("sub")
        if sub is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "无效的凭证")
        return int(sub)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "无效的凭证或已过期")


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "需要登录")
    uid = decode_token(creds.credentials)
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def local_id_from_email(email: str) -> str:
    return email.split("@", 1)[0] if "@" in email else str(email)


def current_week_id() -> int:
    iso = datetime.now(timezone.utc).isocalendar()
    return iso.year * 100 + iso.week


def ordered_user_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def _cross_campus_to_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    if value == "可以接受":
        return True
    if value == "不接受":
        return False
    return None


def compute_match_stats(db: Session, user_id: int) -> dict:
    rows = (
        db.query(Match)
        .filter(or_(Match.user1_id == user_id, Match.user2_id == user_id))
        .all()
    )
    if not rows:
        return {"matches": 0, "bestScore": 0, "weeks": 0}
    best = 0
    weeks_set = set()
    for m in rows:
        sc = m.score
        if sc is not None and sc >= 0:
            best = max(best, int(round(sc)))
        if m.week_number and m.week_number > 0:
            weeks_set.add(m.week_number)
    return {
        "matches": len(rows),
        "bestScore": best,
        "weeks": len(weeks_set),
    }


def has_weekly_match(db: Session, user_id: int, week_id: int) -> bool:
    return (
        db.query(Match)
        .filter(
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.week_number == week_id,
        )
        .first()
        is not None
    )


def serialize_user(db: Session, user: User, login_time_ms: int | None = None) -> dict:
    stats = compute_match_stats(db, user.id)
    weekly = has_weekly_match(db, user.id, current_week_id())
    values = user.values_json if isinstance(user.values_json, list) else []
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "id": local_id_from_email(user.email),
        "email": user.email,
        "name": user.name or "",
        "campus": user.campus or "",
        "grade": user.grade or "",
        "major": user.major or "",
        "bio": user.bio or "",
        "values": values,
        "wechat": user.wechat or "",
        "stats": stats,
        "loggedIn": True,
        "loginTime": login_time_ms if login_time_ms is not None else now_ms,
        "quizCompleted": bool(user.quiz_completed),
        "weeklyMatch": weekly,
        "paused": bool(user.paused),
    }


def peer_from_match(db: Session, m: Match, me_id: int) -> User | None:
    pid = m.user2_id if m.user1_id == me_id else m.user1_id
    return db.query(User).filter(User.id == pid).first()


def messages_for_user(rd: dict, me_id: int, peer_id: int) -> tuple[str | None, str | None]:
    if not rd:
        return None, None
    by_uid = rd.get("messagesByUserId") or {}
    if isinstance(by_uid, dict) and by_uid:
        your = by_uid.get(str(me_id)) or by_uid.get(me_id)
        their = by_uid.get(str(peer_id)) or by_uid.get(peer_id)
        return their, your
    their = rd.get("theirMessage") or rd.get("their_message")
    your = rd.get("yourMessage") or rd.get("your_message")
    return their, your


# --- Routes ---


@app.get("/")
def read_root():
    return {"message": "CSU Date API 已启动"}


@app.post("/api/auth/register")
def auth_register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = normalize_csu_email(body.email)
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "该邮箱已注册")
    user = User(
        email=email,
        hashed_password=hash_password(body.password),
        name=body.name,
        campus=body.campus,
        grade=body.grade,
        major=body.major,
        quiz_completed=False,
        paused=False,
        is_verified=True,
        bio="",
        values_json=[],
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "注册失败")
    db.refresh(user)
    token = create_access_token(user.id)
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(db, user, login_time_ms=now_ms),
    }


@app.post("/api/auth/login")
def auth_login(body: LoginRequest, db: Session = Depends(get_db)):
    email = normalize_csu_email(body.email)
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "邮箱或密码错误")
    token = create_access_token(user.id)
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(db, user, login_time_ms=now_ms),
    }


@app.get("/api/user/me")
def get_me(user: CurrentUser, db: Session = Depends(get_db)):
    return serialize_user(db, user)


@app.post("/api/user/wechat")
def update_wechat(
    body: WechatUpdateRequest,
    user: CurrentUser,
    db: Session = Depends(get_db),
):
    user.wechat = (body.wechat or "").strip()[:64]
    db.commit()
    db.refresh(user)
    return {"ok": True, "user": serialize_user(db, user)}


@app.post("/api/user/paused")
def set_paused(
    body: PausedRequest,
    user: CurrentUser,
    db: Session = Depends(get_db),
):
    user.paused = body.paused
    db.commit()
    db.refresh(user)
    return {"ok": True, "user": serialize_user(db, user)}


@app.post("/api/crush/shoot")
def crush_shoot(
    body: ShootRequest,
    user: CurrentUser,
    db: Session = Depends(get_db),
):
    target_email = normalize_csu_email(body.target_email)
    if target_email == user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不能对自己发射")

    target = db.query(User).filter(User.email == target_email).first()

    existing = (
        db.query(Crush)
        .filter(Crush.sender_id == user.id, Crush.target_email == target_email)
        .order_by(Crush.id.desc())
        .first()
    )
    if existing and existing.is_mutual:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "已与该用户双向匹配")

    if not existing:
        crush = Crush(
            sender_id=user.id,
            target_email=target_email,
            message=(body.message or "")[:2000],
            is_mutual=False,
        )
        db.add(crush)
    else:
        crush = existing
        crush.message = (body.message or "")[:2000]

    mutual = False
    if target:
        inverse = (
            db.query(Crush)
            .filter(
                Crush.sender_id == target.id,
                Crush.target_email == user.email,
            )
            .order_by(Crush.id.desc())
            .first()
        )
        if inverse:
            mutual = True
            crush.is_mutual = True
            inverse.is_mutual = True
            u1, u2 = ordered_user_pair(user.id, target.id)
            dup = (
                db.query(Match)
                .filter(
                    Match.user1_id == u1,
                    Match.user2_id == u2,
                    Match.week_number == 0,
                )
                .first()
            )
            if not dup:
                rd = {
                    "kind": "mutual_shot",
                    "messagesByUserId": {
                        str(user.id): crush.message or "",
                        str(target.id): inverse.message or "",
                    },
                }
                m = Match(
                    user1_id=u1,
                    user2_id=u2,
                    week_number=0,
                    score=100.0,
                    report_data=rd,
                )
                db.add(m)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "匹配记录已存在或数据冲突",
        )

    return {
        "ok": True,
        "mutual": mutual,
        "message": "双向匹配成功" if mutual else "已保存，等待对方也向你发射",
        "user": serialize_user(db, user),
    }


@app.get("/api/inbox")
def get_inbox(user: CurrentUser, db: Session = Depends(get_db)):
    items: list[dict] = []

    matches = (
        db.query(Match)
        .filter(or_(Match.user1_id == user.id, Match.user2_id == user.id))
        .order_by(Match.week_number.desc(), Match.id.desc())
        .all()
    )
    for m in matches:
        peer = peer_from_match(db, m, user.id)
        if not peer:
            continue
        rd = m.report_data if isinstance(m.report_data, dict) else {}
        kind = rd.get("kind", "algorithm")
        their_msg, your_msg = messages_for_user(rd, user.id, peer.id)
        preview = their_msg or your_msg or "匹配记录"
        items.append(
            {
                "id": m.id,
                "type": "mutual",
                "status": "mutual",
                "weekNumber": m.week_number,
                "score": int(round(m.score)) if m.score is not None else None,
                "peerName": peer.name or "CSU 用户",
                "peerEmail": peer.email,
                "peerCampus": peer.campus or "",
                "peerGrade": peer.grade or "",
                "peerMajor": peer.major or "",
                "peerInitial": (peer.name or "?")[:1],
                "peerWechat": peer.wechat or "",
                "theirMessage": their_msg,
                "yourMessage": your_msg,
                "preview": preview,
                "kind": kind,
            }
        )

    pending = (
        db.query(Crush)
        .filter(Crush.sender_id == user.id, Crush.is_mutual.is_(False))
        .order_by(Crush.id.desc())
        .all()
    )
    for c in pending:
        items.append(
            {
                "id": f"crush-{c.id}",
                "type": "waiting",
                "status": "waiting",
                "weekNumber": None,
                "targetEmail": c.target_email,
                "preview": c.message or "已发送 Shoot Your Shot，等待对方也向你发射…",
                "message": c.message or "",
            }
        )

    return {"threads": items}


@app.post("/api/quiz/submit")
def submit_quiz(
    payload: QuizSubmit,
    user: CurrentUser,
    db: Session = Depends(get_db),
):
    cross_ok = _cross_campus_to_bool(payload.crossCampus)

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)

    profile.gender = payload.gender
    profile.sexuality = payload.sexuality
    profile.campus = payload.campus
    profile.cross_campus_ok = cross_ok
    profile.raw_quiz_data = payload.raw_quiz_data

    user.quiz_completed = True
    db.commit()
    db.refresh(profile)
    db.refresh(user)

    return {
        "status": "success",
        "message": "问卷已保存",
        "profile_id": profile.id,
        "user_id": user.id,
        "user": serialize_user(db, user),
    }
