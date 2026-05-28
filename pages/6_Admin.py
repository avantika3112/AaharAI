import streamlit as st
import pandas as pd
import os
import sys
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import (
    admin_delete_user,
    ensure_authenticated,
    get_audit_log_stats,
    get_audit_logs,
    get_current_user,
    is_admin_user,
    render_auth_status,
)
from utils.storage import load_user_data
from utils.ui import apply_base_theme

st.set_page_config(page_title="Admin Panel", page_icon="🛡️", layout="wide")
apply_base_theme()
ensure_authenticated()
render_auth_status()

current_user = get_current_user()
if not is_admin_user(current_user):
    st.error("Admin access only.")
    st.stop()

st.title("🛡️ Admin Panel")
st.caption("Manage users and review app usage stats")
st.divider()

data = load_user_data()
users = data.get("users", {})
user_buckets = data.get("user_buckets", {})

if not isinstance(users, dict):
    users = {}
if not isinstance(user_buckets, dict):
    user_buckets = {}

usernames = sorted(users.keys())

chat_count = 0
meal_plan_count = 0
bmi_count = 0
for username in usernames:
    bucket = user_buckets.get(username, {})
    if not isinstance(bucket, dict):
        continue
    chat_count += len(bucket.get("chat_history", [])) if isinstance(bucket.get("chat_history", []), list) else 0
    meal_plan_count += len(bucket.get("meal_plan_history", [])) if isinstance(bucket.get("meal_plan_history", []), list) else 0
    bmi_count += len(bucket.get("bmi_history", [])) if isinstance(bucket.get("bmi_history", []), list) else 0

admin_users = [u for u in usernames if is_admin_user(u)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users", len(usernames))
col2.metric("Admin Users", len(admin_users))
col3.metric("Saved Meal Plans", meal_plan_count)
col4.metric("BMI Logs", bmi_count)

st.divider()
st.subheader("User Summary")

rows = []
for username in usernames:
    bucket = user_buckets.get(username, {})
    if not isinstance(bucket, dict):
        bucket = {}

    profile = bucket.get("profile", {}) if isinstance(bucket.get("profile", {}), dict) else {}

    rows.append(
        {
            "username": username,
            "role": "admin" if is_admin_user(username) else "user",
            "has_profile": bool(profile),
            "chat_messages": len(bucket.get("chat_history", [])) if isinstance(bucket.get("chat_history", []), list) else 0,
            "saved_plans": len(bucket.get("meal_plan_history", [])) if isinstance(bucket.get("meal_plan_history", []), list) else 0,
            "bmi_logs": len(bucket.get("bmi_history", [])) if isinstance(bucket.get("bmi_history", []), list) else 0,
        }
    )

if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("No users found yet.")

st.divider()
st.subheader("Danger Zone")

c1, c2 = st.columns([2, 1])
with c1:
    delete_target = st.selectbox("Select user to delete", [""] + usernames)
with c2:
    confirm_delete = st.checkbox("I understand this is permanent")

if st.button("Delete Selected User", type="primary", use_container_width=True):
    if not delete_target:
        st.error("Select a user first.")
    elif delete_target == current_user:
        st.error("You cannot delete your own account from admin panel.")
    elif is_admin_user(delete_target):
        st.error("Cannot delete another admin from here.")
    elif not confirm_delete:
        st.error("Please confirm permanent deletion.")
    else:
        ok, message = admin_delete_user(delete_target, actor=current_user)
        if ok:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

st.divider()
st.subheader("Audit Logs")

audit_logs = list(reversed(get_audit_logs(limit=0)))
if audit_logs:
    logs_df = pd.DataFrame(audit_logs)
    stats = get_audit_log_stats()
    m1, m2 = st.columns(2)
    m1.metric("Active Logs", stats.get("active", 0))
    m2.metric("Archived Logs", stats.get("archived", 0))

    # Normalize columns and datetime for robust filtering.
    for column in ["ts", "action", "status", "actor", "target", "details"]:
        if column not in logs_df.columns:
            logs_df[column] = ""
    logs_df["ts"] = pd.to_datetime(logs_df["ts"], errors="coerce")
    logs_df = logs_df.sort_values(by="ts", ascending=False, na_position="last")

    st.markdown("### Filter Logs")
    if "admin_audit_preset" not in st.session_state:
        st.session_state["admin_audit_preset"] = "Custom"

    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        if st.button("Custom", use_container_width=True):
            st.session_state["admin_audit_preset"] = "Custom"
    with p2:
        if st.button("Today", use_container_width=True):
            st.session_state["admin_audit_preset"] = "Today"
    with p3:
        if st.button("Last 7 Days", use_container_width=True):
            st.session_state["admin_audit_preset"] = "Last 7 Days"
    with p4:
        if st.button("Last 24 Hours", use_container_width=True):
            st.session_state["admin_audit_preset"] = "Last 24 Hours"
    with p5:
        if st.button("Failed Only", use_container_width=True):
            st.session_state["admin_audit_preset"] = "Failed Only"

    active_preset = st.session_state.get("admin_audit_preset", "Custom")
    st.caption(f"Preset: {active_preset}")

    f1, f2, f3 = st.columns(3)
    with f1:
        action_options = ["All"] + sorted(logs_df["action"].dropna().astype(str).unique().tolist())
        action_filter = st.selectbox("Action", action_options)
    with f2:
        status_options = ["All"] + sorted(logs_df["status"].dropna().astype(str).unique().tolist())
        status_filter = st.selectbox("Status", status_options)
    with f3:
        actor_options = ["All"] + sorted(logs_df["actor"].dropna().astype(str).unique().tolist())
        actor_filter = st.selectbox("Actor", actor_options)

    f4, f5, f6 = st.columns(3)
    with f4:
        target_options = ["All"] + sorted(logs_df["target"].dropna().astype(str).unique().tolist())
        target_filter = st.selectbox("Target", target_options)
    with f5:
        valid_ts = logs_df["ts"].dropna()
        if not valid_ts.empty:
            min_day = valid_ts.min().date()
            max_day = valid_ts.max().date()
            date_range = st.date_input("Date Range", value=(min_day, max_day), min_value=min_day, max_value=max_day)
        else:
            date_range = ()
            st.caption("No valid timestamps available for date filtering.")
    with f6:
        keyword = st.text_input("Keyword", placeholder="Search details, actor, or target")

    filtered_df = logs_df.copy()

    today = date.today()
    if active_preset == "Today":
        filtered_df = filtered_df[filtered_df["ts"].dt.date == today]
    elif active_preset == "Last 7 Days":
        start_date = today - timedelta(days=6)
        filtered_df = filtered_df[
            filtered_df["ts"].notna() & (filtered_df["ts"].dt.date >= start_date) & (filtered_df["ts"].dt.date <= today)
        ]
    elif active_preset == "Last 24 Hours":
        cutoff = pd.Timestamp.now() - pd.Timedelta(hours=24)
        filtered_df = filtered_df[filtered_df["ts"].notna() & (filtered_df["ts"] >= cutoff)]
    elif active_preset == "Failed Only":
        filtered_df = filtered_df[filtered_df["status"] == "failed"]

    if action_filter != "All":
        filtered_df = filtered_df[filtered_df["action"] == action_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]
    if actor_filter != "All":
        filtered_df = filtered_df[filtered_df["actor"] == actor_filter]
    if target_filter != "All":
        filtered_df = filtered_df[filtered_df["target"] == target_filter]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filtered_df = filtered_df[
            filtered_df["ts"].isna() | ((filtered_df["ts"] >= start_ts) & (filtered_df["ts"] <= end_ts))
        ]

    if keyword:
        pattern = keyword.strip()
        text_mask = (
            filtered_df["details"].astype(str).str.contains(pattern, case=False, na=False)
            | filtered_df["actor"].astype(str).str.contains(pattern, case=False, na=False)
            | filtered_df["target"].astype(str).str.contains(pattern, case=False, na=False)
        )
        filtered_df = filtered_df[text_mask]

    page_col_1, page_col_2 = st.columns([1, 1])
    with page_col_1:
        page_size = st.selectbox("Rows per page", [25, 50, 100, 200], index=1)
    with page_col_2:
        total_pages = max(1, (len(filtered_df) + page_size - 1) // page_size)
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (int(page) - 1) * page_size
    end_idx = start_idx + page_size
    paged_df = filtered_df.iloc[start_idx:end_idx]

    shown_start = 0 if len(filtered_df) == 0 else start_idx + 1
    shown_end = min(end_idx, len(filtered_df))
    st.caption(f"Showing {shown_start}-{shown_end} of {len(filtered_df)} filtered logs (from {len(logs_df)} total)")
    st.dataframe(paged_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download Filtered Audit Logs",
        data=filtered_df.to_csv(index=False),
        file_name="aaharai_audit_logs_filtered.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.info("No audit logs available yet.")
