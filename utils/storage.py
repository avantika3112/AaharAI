import json
from pathlib import Path
from typing import Any, Dict


DATA_FILE = Path(__file__).resolve().parent.parent / "user_data.json"


def load_user_data() -> Dict[str, Any]:
    """Load persisted user data safely; return empty dict if file is missing/corrupt."""
    if not DATA_FILE.exists():
        return {}

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_user_data(data: Dict[str, Any]) -> None:
    """Write complete user data payload to disk."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def update_user_data(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge partial updates into persisted user data and return merged payload."""
    data = load_user_data()
    data.update(updates)
    save_user_data(data)
    return data


def append_to_user_list(key: str, item: Any, limit: int = 20) -> Dict[str, Any]:
    """Append an item to a list key in persisted data and cap list size."""
    data = load_user_data()
    current = data.get(key, [])
    if not isinstance(current, list):
        current = []

    current.append(item)
    if limit > 0:
        current = current[-limit:]

    data[key] = current
    save_user_data(data)
    return data


def load_user_bucket(username: str) -> Dict[str, Any]:
    """Load user-scoped app data bucket."""
    if not username:
        return {}
    data = load_user_data()
    user_buckets = data.get("user_buckets", {})
    if not isinstance(user_buckets, dict):
        return {}
    bucket = user_buckets.get(username, {})
    return bucket if isinstance(bucket, dict) else {}


def update_user_bucket(username: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge updates into a user-scoped app data bucket."""
    if not username:
        return {}
    data = load_user_data()
    user_buckets = data.get("user_buckets", {})
    if not isinstance(user_buckets, dict):
        user_buckets = {}
    bucket = user_buckets.get(username, {})
    if not isinstance(bucket, dict):
        bucket = {}
    bucket.update(updates)
    user_buckets[username] = bucket
    data["user_buckets"] = user_buckets
    save_user_data(data)
    return bucket


def append_to_user_bucket_list(username: str, key: str, item: Any, limit: int = 20) -> Dict[str, Any]:
    """Append an item to a list inside a user-scoped bucket."""
    bucket = load_user_bucket(username)
    current = bucket.get(key, [])
    if not isinstance(current, list):
        current = []

    current.append(item)
    if limit > 0:
        current = current[-limit:]

    return update_user_bucket(username, {key: current})


def delete_user_bucket(username: str) -> Dict[str, Any]:
    """Delete a user-scoped bucket if it exists."""
    if not username:
        return {}

    data = load_user_data()
    user_buckets = data.get("user_buckets", {})
    if isinstance(user_buckets, dict) and username in user_buckets:
        user_buckets.pop(username, None)
        data["user_buckets"] = user_buckets
        save_user_data(data)

    return data
