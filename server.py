import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

DB = os.getenv("RESOLVE_DB", "resolve.db")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

app = FastAPI(title="RESOLVE API", version="1.7")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


SCHEMA_SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS users(
    id TEXT PRIMARY KEY,
    name TEXT,
    phone TEXT UNIQUE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts(
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS cases(
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    contact_id TEXT,
    title TEXT NOT NULL,
    type TEXT,
    status TEXT NOT NULL,
    value_cents INTEGER DEFAULT 0,
    balance_cents INTEGER DEFAULT 0,
    next_step TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(contact_id) REFERENCES contacts(id)
);
CREATE TABLE IF NOT EXISTS events(
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    type TEXT NOT NULL,
    text TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(case_id) REFERENCES cases(id)
);
CREATE TABLE IF NOT EXISTS payments(
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    direction TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(case_id) REFERENCES cases(id)
);
CREATE TABLE IF NOT EXISTS actions(
    id TEXT PRIMARY KEY,
    case_id TEXT,
    intent TEXT NOT NULL,
    risk_level INTEGER NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL,
    confirmed_at TEXT,
    FOREIGN KEY(case_id) REFERENCES cases(id)
);
CREATE TABLE IF NOT EXISTS audit_log(
    id TEXT PRIMARY KEY,
    action_id TEXT,
    event TEXT NOT NULL,
    detail TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(action_id) REFERENCES actions(id)
);
CREATE TABLE IF NOT EXISTS messages(
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    sender TEXT NOT NULL,
    text TEXT NOT NULL,
    intent_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""


class InterpretRequest(BaseModel):
    sender: str
    text: str


def init_db() -> None:
    conn = get_db()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup() -> None:
    init_db()


def get_or_create_user(conn: sqlite3.Connection, sender: str) -> str:
    row = conn.execute("SELECT id FROM users WHERE phone=?", (sender,)).fetchone()
    if row:
        return row["id"]
    user_id = uid("user")
    conn.execute(
        "INSERT INTO users(id,name,phone,created_at) VALUES(?,?,?,?)",
        (user_id, sender, sender, now()),
    )
    return user_id


def memory(conn: sqlite3.Connection, user_id: str) -> dict[str, Any]:
    cases = [
        dict(row)
        for row in conn.execute(
            """
            SELECT c.*, ct.name AS contact_name
            FROM cases c
            LEFT JOIN contacts ct ON ct.id=c.contact_id
            WHERE c.user_id=?
            ORDER BY c.updated_at DESC
            LIMIT 50
            """,
            (user_id,),
        )
    ]
    events = [
        dict(row)
        for row in conn.execute(
            """
            SELECT e.*, c.title
            FROM events e
            JOIN cases c ON c.id=e.case_id
            WHERE c.user_id=?
            ORDER BY e.created_at DESC
            LIMIT 50
            """,
            (user_id,),
        )
    ]
    messages = [
        dict(row)
        for row in conn.execute(
            """
            SELECT id,channel,sender,text,intent_json,created_at
            FROM messages
            WHERE user_id=?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (user_id,),
        )
    ]
    return {"cases": cases, "recent_events": events, "recent_messages": messages}


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "CONSULTAR_SALDO",
                "REGISTRAR_PAGAMENTO",
                "REGISTRAR_EVENTO",
                "PREPARAR_MENSAGEM",
                "CONSULTAR_CASO",
                "REGISTRAR_INFORMACAO",
                "PEDIR_ESCLARECIMENTO",
            ],
        },
        "contact_name": {"type": ["string", "null"]},
        "case_id": {"type": ["string", "null"]},
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"type": {"type": "string"}, "value": {"type": "string"}},
                "required": ["type", "value"],
            },
        },
        "date_reference": {"type": ["string", "null"]},
        "amount_cents": {"type": ["integer", "null"]},
        "confidence": {"type": "string", "enum": ["ALTA", "MEDIA", "BAIXA"]},
        "risk_level": {"type": "integer", "enum": [0, 1, 2, 3, 4]},
        "needs_confirmation": {"type": "boolean"},
        "clarifying_question": {"type": ["string", "null"]},
        "reply": {"type": "string"},
        "consequences": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "intent",
        "contact_name",
        "case_id",
        "entities",
        "date_reference",
        "amount_cents",
        "confidence",
        "risk_level",
        "needs_confirmation",
        "clarifying_question",
        "reply",
        "consequences",
    ],
}


def fallback(text: str, mem: dict[str, Any]) -> dict[str, Any]:
    cases = mem["cases"]
    hits = [
        c for c in cases
        if c.get("contact_name") and re.search(r"\b" + re.escape(c["contact_name"]) + r"\b", text, re.I)
    ]
    if len(hits) != 1:
        return {
            "intent": "PEDIR_ESCLARECIMENTO",
            "contact_name": None,
            "case_id": None,
            "entities": [],
            "date_reference": None,
            "amount_cents": None,
            "confidence": "BAIXA",
            "risk_level": 0,
            "needs_confirmation": False,
            "clarifying_question": "Qual pessoa ou caso você quer usar?",
            "reply": "Preciso identificar o caso antes de continuar.",
            "consequences": [],
            "ai_used": False,
        }
    case = hits[0]
    low = text.lower()
    if re.search(r"\b(quanto|deve|saldo|falta|restante)\b", low):
        value = (case.get("balance_cents") or 0) / 100
        br = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return {
            "intent": "CONSULTAR_SALDO",
            "contact_name": case["contact_name"],
            "case_id": case["id"],
            "entities": [],
            "date_reference": None,
            "amount_cents": None,
            "confidence": "ALTA",
            "risk_level": 0,
            "needs_confirmation": False,
            "clarifying_question": None,
            "reply": f"O saldo deste caso é {br}.",
            "consequences": [],
            "ai_used": False,
        }
    if re.search(r"\b(manda|envia|enviar|mensagem|cobrança|cobre)\b", low):
        return {
            "intent": "PREPARAR_MENSAGEM",
            "contact_name": case["contact_name"],
            "case_id": case["id"],
            "entities": [],
            "date_reference": None,
            "amount_cents": None,
            "confidence": "ALTA",
            "risk_level": 2,
            "needs_confirmation": True,
            "clarifying_question": None,
            "reply": "Posso preparar a mensagem, mas ela só deve ser enviada após confirmação.",
            "consequences": ["criar ação externa pendente"],
            "ai_used": False,
        }
    return {
        "intent": "REGISTRAR_INFORMACAO",
        "contact_name": case["contact_name"],
        "case_id": case["id"],
        "entities": [],
        "date_reference": None,
        "amount_cents": None,
        "confidence": "MEDIA",
        "risk_level": 0,
        "needs_confirmation": False,
        "clarifying_question": None,
        "reply": f"Associei a mensagem ao caso de {case['contact_name']}.",
        "consequences": [],
        "ai_used": False,
    }


def ai_interpret(text: str, mem: dict[str, Any]) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = f"""Você é o interpretador do RESOLVE.
O RESOLVE acompanha situações, consequências e próximos passos.
Nunca invente fatos. Use somente a mensagem e a memória fornecida.
Se houver ambiguidade de identidade, dinheiro ou ação externa, escolha PEDIR_ESCLARECIMENTO.
Você interpreta; o sistema valida, decide e autoriza ações.

MEMÓRIA DISPONÍVEL:
{json.dumps(mem, ensure_ascii=False, indent=2)}

MENSAGEM:
{text}

Retorne somente o objeto estruturado solicitado."""
        response = client.responses.create(
            model=MODEL,
            instructions="Interprete mensagens em português do Brasil para o sistema RESOLVE. Seja conservador com identidade, dinheiro e ações externas.",
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "resolve_interpretation",
                    "strict": True,
                    "schema": SCHEMA,
                }
            },
        )
        return json.loads(response.output_text)
    except Exception as exc:
        # Do not expose secrets or request headers in the API response.
        return {"_ai_error": str(exc)}


def guardrail(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("_ai_error"):
        return {"_ai_used": False, "_ai_error": result["_ai_error"]}
    if result.get("risk_level", 0) >= 2:
        result["needs_confirmation"] = True
    if result.get("intent") == "PEDIR_ESCLARECIMENTO":
        result["needs_confirmation"] = False
    if result.get("confidence") == "BAIXA":
        result["needs_confirmation"] = False
    result["ai_used"] = True
    return result


def process(sender: str, text: str, channel: str = "API") -> dict[str, Any]:
    if not sender.strip() or not text.strip():
        raise HTTPException(status_code=400, detail="sender e text são obrigatórios")

    conn = get_db()
    user_id = get_or_create_user(conn, sender.strip())
    mem = memory(conn, user_id)
    result = ai_interpret(text, mem)

    if result is None:
        result = fallback(text, mem)
    else:
        result = guardrail(result)
        if result.get("_ai_error"):
            # Keep the API usable without turning a provider error into a fake answer.
            fallback_result = fallback(text, mem)
            fallback_result["ai_used"] = False
            fallback_result["ai_error"] = result["_ai_error"]
            result = fallback_result

    conn.execute(
        "INSERT INTO messages(id,user_id,channel,sender,text,intent_json,created_at) VALUES(?,?,?,?,?,?,?)",
        (uid("msg"), user_id, channel, sender, text, json.dumps(result, ensure_ascii=False), now()),
    )

    if result.get("needs_confirmation") and result.get("intent") == "PREPARAR_MENSAGEM":
        action_id = uid("act")
        conn.execute(
            "INSERT INTO actions(id,case_id,intent,risk_level,status,payload_json,created_at,confirmed_at) VALUES(?,?,?,?,?,?,?,?)",
            (
                action_id,
                result.get("case_id"),
                result["intent"],
                result.get("risk_level", 2),
                "PENDENTE",
                json.dumps({"source_text": text, "reply": result.get("reply", "")}, ensure_ascii=False),
                now(),
                None,
            ),
        )
        conn.execute(
            "INSERT INTO audit_log(id,action_id,event,detail,created_at) VALUES(?,?,?,?,?)",
            (uid("audit"), action_id, "ACTION_CREATED", "Ação externa criada como PENDENTE; nenhum envio executado.", now()),
        )

    conn.commit()
    conn.close()
    return result


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "resolve",
        "version": "1.7",
        "model": MODEL,
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.get("/memory")
def get_memory(sender: str) -> dict[str, Any]:
    conn = get_db()
    row = conn.execute("SELECT id FROM users WHERE phone=?", (sender,)).fetchone()
    if not row:
        conn.close()
        return {"cases": [], "recent_events": [], "recent_messages": []}
    data = memory(conn, row["id"])
    conn.close()
    return data


@app.get("/actions")
def get_actions(sender: str) -> list[dict[str, Any]]:
    conn = get_db()
    row = conn.execute("SELECT id FROM users WHERE phone=?", (sender,)).fetchone()
    if not row:
        conn.close()
        return []
    rows = conn.execute(
        """
        SELECT a.* FROM actions a
        LEFT JOIN cases c ON c.id=a.case_id
        WHERE c.user_id=? OR a.case_id IS NULL
        ORDER BY a.created_at DESC LIMIT 100
        """,
        (row["id"],),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/interpret")
def interpret(body: InterpretRequest) -> dict[str, Any]:
    return process(body.sender, body.text, "API")


@app.post("/webhook/whatsapp")
async def whatsapp(request: Request) -> dict[str, Any]:
    payload = await request.json()
    text = payload.get("text")
    sender = payload.get("sender")
    if not text or not sender:
        raise HTTPException(status_code=400, detail="sender e text são obrigatórios")
    return process(str(sender), str(text), "WHATSAPP")
