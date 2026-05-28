import bcrypt
import os
from datetime import datetime
import streamlit as st

from utils.storage import delete_user_bucket, load_user_data, save_user_data


USERS_KEY = "users"


def _normalize_username(username: str) -> str:
    return username.strip().lower()


def _password_valid(password: str) -> bool:
    return len(password) >= 6


def _admin_usernames() -> set[str]:
    configured = os.getenv("AAHARAI_ADMIN_USERS", "admin")
    return {item.strip().lower() for item in configured.split(",") if item.strip()}


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(0, value)


def _log_auth_event(
    action: str,
    status: str,
    actor: str = "",
    target: str = "",
    details: str = "",
) -> None:
    active_limit = _get_int_env("AAHARAI_AUDIT_ACTIVE_LIMIT", 1000)
    archive_limit = _get_int_env("AAHARAI_AUDIT_ARCHIVE_LIMIT", 10000)

    data = load_user_data()
    logs = data.get("audit_logs", [])
    archive = data.get("audit_logs_archive", [])
    if not isinstance(logs, list):
        logs = []
    if not isinstance(archive, list):
        archive = []

    logs.append(
        {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "status": status,
            "actor": _normalize_username(actor) if actor else "",
            "target": _normalize_username(target) if target else "",
            "details": details,
        }
    )

    if active_limit > 0 and len(logs) > active_limit:
        overflow = len(logs) - active_limit
        archive.extend(logs[:overflow])
        logs = logs[-active_limit:]

    if archive_limit > 0 and len(archive) > archive_limit:
        archive = archive[-archive_limit:]

    data["audit_logs"] = logs
    data["audit_logs_archive"] = archive
    save_user_data(data)


def _load_users() -> dict:
    data = load_user_data()
    users = data.get(USERS_KEY, {})
    return users if isinstance(users, dict) else {}


def _save_users(users: dict) -> None:
    data = load_user_data()
    data[USERS_KEY] = users
    save_user_data(data)


def register_user(username: str, password: str) -> tuple[bool, str]:
    username = _normalize_username(username)
    if len(username) < 3:
        _log_auth_event("register", "failed", actor=username, details="username too short")
        return False, "Username must be at least 3 characters."
    if not _password_valid(password):
        _log_auth_event("register", "failed", actor=username, details="password too short")
        return False, "Password must be at least 6 characters."

    users = _load_users()
    if username in users:
        _log_auth_event("register", "failed", actor=username, details="username exists")
        return False, "Username already exists."

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users[username] = {"password": hashed}
    _save_users(users)
    _log_auth_event("register", "success", actor=username)
    return True, "Account created successfully."


def register_user_with_recovery(username: str, password: str, recovery_answer: str) -> tuple[bool, str]:
    username = _normalize_username(username)
    recovery_answer = recovery_answer.strip().lower()
    ok, message = register_user(username, password)
    if not ok:
        return ok, message

    if len(recovery_answer) < 3:
        return True, "Account created. Add a recovery answer later from account settings."

    users = _load_users()
    user = users.get(username, {})
    user["recovery_answer"] = bcrypt.hashpw(
        recovery_answer.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    users[username] = user
    _save_users(users)
    return True, "Account created successfully."


def login_user(username: str, password: str) -> tuple[bool, str]:
    username = _normalize_username(username)
    users = _load_users()
    user = users.get(username)

    if not user:
        _log_auth_event("login", "failed", actor=username, details="user not found")
        return False, "User not found."

    stored_hash = user.get("password", "")
    if not stored_hash:
        _log_auth_event("login", "failed", actor=username, details="missing password hash")
        return False, "Invalid account configuration."

    is_valid = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    if not is_valid:
        _log_auth_event("login", "failed", actor=username, details="incorrect password")
        return False, "Incorrect password."

    st.session_state["is_authenticated"] = True
    st.session_state["username"] = username
    _log_auth_event("login", "success", actor=username)
    return True, "Logged in successfully."


def logout_user() -> None:
    st.session_state["is_authenticated"] = False
    st.session_state["username"] = ""


def get_current_user() -> str:
    return st.session_state.get("username", "")


def is_admin_user(username: str) -> bool:
    return _normalize_username(username) in _admin_usernames()


def _set_password(username: str, new_password: str) -> tuple[bool, str]:
    if not _password_valid(new_password):
        _log_auth_event("set_password", "failed", actor=username, details="password too short")
        return False, "Password must be at least 6 characters."

    users = _load_users()
    user = users.get(username)
    if not user:
        _log_auth_event("set_password", "failed", actor=username, details="user not found")
        return False, "User not found."

    user["password"] = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    users[username] = user
    _save_users(users)
    _log_auth_event("set_password", "success", actor=username)
    return True, "Password updated successfully."


def reset_password_with_recovery(username: str, recovery_answer: str, new_password: str) -> tuple[bool, str]:
    username = _normalize_username(username)
    recovery_answer = recovery_answer.strip().lower()
    users = _load_users()
    user = users.get(username)

    if not user:
        _log_auth_event("reset_password", "failed", actor=username, details="user not found")
        return False, "User not found."

    stored_recovery_hash = user.get("recovery_answer", "")
    if not stored_recovery_hash:
        _log_auth_event("reset_password", "failed", actor=username, details="missing recovery answer")
        return False, "No recovery answer found. Please contact admin or login and set one."

    valid = bcrypt.checkpw(recovery_answer.encode("utf-8"), stored_recovery_hash.encode("utf-8"))
    if not valid:
        _log_auth_event("reset_password", "failed", actor=username, details="incorrect recovery answer")
        return False, "Recovery answer is incorrect."

    _log_auth_event("reset_password", "success", actor=username)
    return _set_password(username, new_password)


def change_password(username: str, current_password: str, new_password: str) -> tuple[bool, str]:
    username = _normalize_username(username)
    users = _load_users()
    user = users.get(username)
    if not user:
        _log_auth_event("change_password", "failed", actor=username, details="user not found")
        return False, "User not found."

    stored_hash = user.get("password", "")
    if not stored_hash or not bcrypt.checkpw(current_password.encode("utf-8"), stored_hash.encode("utf-8")):
        _log_auth_event("change_password", "failed", actor=username, details="incorrect current password")
        return False, "Current password is incorrect."

    _log_auth_event("change_password", "success", actor=username)
    return _set_password(username, new_password)


def delete_account(username: str, password: str) -> tuple[bool, str]:
    username = _normalize_username(username)
    users = _load_users()
    user = users.get(username)
    if not user:
        _log_auth_event("delete_account", "failed", actor=username, target=username, details="user not found")
        return False, "User not found."

    stored_hash = user.get("password", "")
    if not stored_hash or not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        _log_auth_event("delete_account", "failed", actor=username, target=username, details="incorrect password")
        return False, "Password is incorrect."

    users.pop(username, None)
    _save_users(users)
    delete_user_bucket(username)

    if st.session_state.get("username") == username:
        logout_user()
        for key in [
            "profile",
            "bmi_history",
            "meal_plan",
            "chat_history",
            "data_loaded_for",
            "chat_loaded_for",
        ]:
            st.session_state.pop(key, None)

    _log_auth_event("delete_account", "success", actor=username, target=username)
    return True, "Account deleted successfully."


def admin_delete_user(username: str, actor: str = "") -> tuple[bool, str]:
    username = _normalize_username(username)
    actor = _normalize_username(actor) if actor else ""
    users = _load_users()
    if username not in users:
        _log_auth_event("admin_delete_user", "failed", actor=actor, target=username, details="user not found")
        return False, "User not found."

    users.pop(username, None)
    _save_users(users)
    delete_user_bucket(username)
    _log_auth_event("admin_delete_user", "success", actor=actor, target=username)
    return True, f"Deleted user: {username}"


def get_audit_logs(limit: int = 200) -> list[dict]:
    logs = load_user_data().get("audit_logs", [])
    if not isinstance(logs, list):
        return []
    if limit <= 0:
        return logs
    return logs[-limit:]


def get_audit_log_stats() -> dict:
    data = load_user_data()
    active = data.get("audit_logs", [])
    archived = data.get("audit_logs_archive", [])
    if not isinstance(active, list):
        active = []
    if not isinstance(archived, list):
        archived = []
    return {
        "active": len(active),
        "archived": len(archived),
    }


def ensure_authenticated() -> None:
    if st.session_state.get("is_authenticated", False):
        return

    st.title("🔐 Login to AaharAI")
    st.caption("Create an account or login to continue.")

    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])

    with tab1:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary", use_container_width=True):
            ok, message = login_user(login_username, login_password)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with tab2:
        signup_username = st.text_input("Choose Username", key="signup_username")
        signup_password = st.text_input("Choose Password", type="password", key="signup_password")
        recovery_answer = st.text_input(
            "Recovery Answer (for password reset)",
            key="signup_recovery_answer",
            help="Example: your favorite fruit. Keep it memorable.",
        )
        if st.button("Create Account", use_container_width=True):
            ok, message = register_user_with_recovery(signup_username, signup_password, recovery_answer)
            if ok:
                st.success(message)
            else:
                st.error(message)

    with tab3:
        reset_username = st.text_input("Username", key="reset_username")
        reset_answer = st.text_input("Recovery Answer", key="reset_recovery_answer")
        new_password = st.text_input("New Password", type="password", key="reset_new_password")
        confirm_password = st.text_input("Confirm New Password", type="password", key="reset_confirm_password")
        if st.button("Reset Password", use_container_width=True):
            if new_password != confirm_password:
                st.error("New password and confirm password must match.")
            else:
                ok, message = reset_password_with_recovery(reset_username, reset_answer, new_password)
                if ok:
                    st.success(message)
                else:
                    st.error(message)

    st.stop()


def render_auth_status() -> None:
    username = get_current_user()
    if username:
        st.sidebar.success(f"Logged in as: {username}")

        with st.sidebar.expander("🔐 Account Settings", expanded=False):
            current_password = st.text_input("Current password", type="password", key="change_pwd_current")
            new_password = st.text_input("New password", type="password", key="change_pwd_new")
            if st.button("Update Password", use_container_width=True, key="btn_update_password"):
                ok, message = change_password(username, current_password, new_password)
                if ok:
                    st.success(message)
                else:
                    st.error(message)

            st.caption("Delete account permanently")
            delete_stage_key = f"delete_stage_{username}"
            if st.button("Start Account Deletion", use_container_width=True, key="btn_delete_stage_start"):
                st.session_state[delete_stage_key] = True

            if st.session_state.get(delete_stage_key, False):
                st.warning("Final step: this action is irreversible.")
                st.caption(f"Type this exactly: DELETE {username}")
                confirm_phrase = st.text_input(
                    "Confirmation phrase",
                    key="delete_confirm_phrase",
                    help="This prevents accidental account deletion.",
                )
                delete_password = st.text_input("Password", type="password", key="delete_account_password")
                confirm_delete = st.checkbox("I understand all my data will be permanently deleted", key="delete_confirm_checkbox")

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Confirm Permanent Delete", use_container_width=True, key="btn_delete_account_confirm"):
                        if confirm_phrase.strip() != f"DELETE {username}":
                            st.error("Confirmation phrase is incorrect.")
                        elif not confirm_delete:
                            st.error("Please confirm permanent deletion.")
                        else:
                            ok, message = delete_account(username, delete_password)
                            if ok:
                                st.session_state.pop(delete_stage_key, None)
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                with col_b:
                    if st.button("Cancel", use_container_width=True, key="btn_delete_account_cancel"):
                        st.session_state.pop(delete_stage_key, None)
                        st.rerun()

        if st.sidebar.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()
