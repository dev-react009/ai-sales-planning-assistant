import json
import uuid
from app.database import get_connection


def init_chat_tables():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT DEFAULT 'New Chat',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    route VARCHAR(50),
                    sources JSONB DEFAULT '[]'::jsonb,
                    tools_used JSONB DEFAULT '[]'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );

                ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS conversation_id TEXT;
                """
            )
        connection.commit()


def get_conversations(limit: int = 30):
    init_chat_tables()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM chat_conversations
                ORDER BY updated_at DESC
                LIMIT %s;
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "updated_at": row[3].isoformat() if row[3] else None,
                }
                for row in rows
            ]


def create_conversation(title: str = "New Chat", conversation_id: str | None = None):
    init_chat_tables()
    conv_id = conversation_id or str(uuid.uuid4())
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO chat_conversations (id, title, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET updated_at = NOW();
                """,
                (conv_id, title),
            )
        connection.commit()
    return conv_id


def get_chat_messages(conversation_id: str | None = None, limit: int = 100):
    init_chat_tables()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if conversation_id:
                cursor.execute(
                    """
                    SELECT id, role, content, route, sources, tools_used, created_at, conversation_id
                    FROM chat_messages
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC
                    LIMIT %s;
                    """,
                    (conversation_id, limit),
                )
            else:
                # If no conversation specified, fetch the most recent conversation's messages
                cursor.execute(
                    """
                    SELECT id, role, content, route, sources, tools_used, created_at, conversation_id
                    FROM chat_messages
                    WHERE conversation_id = (
                        SELECT id FROM chat_conversations ORDER BY updated_at DESC LIMIT 1
                    ) OR conversation_id IS NULL
                    ORDER BY created_at ASC
                    LIMIT %s;
                    """,
                    (limit,),
                )

            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "role": row[1],
                    "content": row[2],
                    "route": row[3],
                    "sources": row[4] if isinstance(row[4], list) else (json.loads(row[4]) if row[4] else []),
                    "tools_used": row[5] if isinstance(row[5], list) else (json.loads(row[5]) if row[5] else []),
                    "created_at": row[6].isoformat() if row[6] else None,
                    "conversation_id": row[7],
                }
                for row in rows
            ]


def save_chat_message(
    role: str,
    content: str,
    conversation_id: str | None = None,
    route: str | None = None,
    sources: list[str] | None = None,
    tools_used: list[str] | None = None,
    message_id: str | None = None,
):
    init_chat_tables()
    msg_id = message_id or str(uuid.uuid4())
    sources_json = json.dumps(sources or [])
    tools_json = json.dumps(tools_used or [])

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO chat_messages (id, conversation_id, role, content, route, sources, tools_used)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    route = EXCLUDED.route,
                    sources = EXCLUDED.sources,
                    tools_used = EXCLUDED.tools_used;
                """,
                (msg_id, conversation_id, role, content, route, sources_json, tools_json),
            )
            if conversation_id:
                cursor.execute(
                    """
                    UPDATE chat_conversations SET updated_at = NOW() WHERE id = %s;
                    """,
                    (conversation_id,),
                )
        connection.commit()
    return msg_id


def delete_conversation(conversation_id: str):
    init_chat_tables()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM chat_messages WHERE conversation_id = %s;", (conversation_id,))
            cursor.execute("DELETE FROM chat_conversations WHERE id = %s;", (conversation_id,))
        connection.commit()


def clear_chat_messages(conversation_id: str | None = None):
    init_chat_tables()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if conversation_id:
                cursor.execute("DELETE FROM chat_messages WHERE conversation_id = %s;", (conversation_id,))
                cursor.execute("DELETE FROM chat_conversations WHERE id = %s;", (conversation_id,))
            else:
                cursor.execute("DELETE FROM chat_messages;")
                cursor.execute("DELETE FROM chat_conversations;")
        connection.commit()
