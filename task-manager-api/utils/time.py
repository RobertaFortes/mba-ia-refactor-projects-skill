from datetime import datetime, timezone


def utcnow():
    """Data/hora UTC "naive" (mesmo formato armazenado antes), sem usar o datetime.utcnow() deprecated."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
