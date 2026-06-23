from __future__ import annotations

import os
from dataclasses import dataclass

import psycopg


@dataclass(frozen=True)
class DbConfig:
    host: str = "127.0.0.1"
    port: int = 5432
    dbname: str = "wiki_game"
    user: str = "wiki_game_user"
    password: str | None = None

    @classmethod
    def from_env(cls) -> "DbConfig":
        password = os.getenv("WIKIGAME_DB_PASSWORD") or os.getenv("PGPASSWORD")
        return cls(
            host=os.getenv("WIKIGAME_DB_HOST", "127.0.0.1"),
            port=int(os.getenv("WIKIGAME_DB_PORT", "5432")),
            dbname=os.getenv("WIKIGAME_DB_NAME", "wiki_game"),
            user=os.getenv("WIKIGAME_DB_USER", "wiki_game_user"),
            password=password,
        )

    def connect(self) -> psycopg.Connection:
        kwargs: dict[str, object] = {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
        }
        if self.password is not None:
            kwargs["password"] = self.password
        return psycopg.connect(**kwargs)
