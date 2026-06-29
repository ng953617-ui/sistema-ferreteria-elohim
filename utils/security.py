"""Utilidades de seguridad para Ferretería Elohim."""
from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Genera un hash bcrypt para guardar contraseñas de forma segura."""
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """Valida una contraseña contra su hash bcrypt."""
    if not password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False
