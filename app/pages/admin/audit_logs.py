"""
Admin – Audit Logs
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query
from app.core.utils import section_header, fmt_datetime


def show():
    user = require_auth(["admin"])
    section_header("📋 Audit Logs", "Track all system actions and events")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search by action or entity", placeholder="e.g. login, report…")
    with col2:
        status_filter = st.selectbox("Status", ["all","success","error"])
    with col3:
        limit = st.selectbox("Show", [50, 100, 200, 500], index=0)

    try:
        base_sql = """
            SELECT al.id, al.action, al.entity_type, al.entity_id,
                   al.status, al.ip_address, al.created_at,
                   COALESCE(u.full_name, 'System') as user_name,
                   u.role
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE 1=1
        """
        params = {}
        if status_filter != "all":
            base_sql += " AND al.status=:status"
            params["status"] = status_filter
        if search:
            base_sql += " AND (LOWER(al.action) LIKE :search OR LOWER(al.entity_type) LIKE :search)"
            params["search"] = f"%{search.lower()}%"
        base_sql += " ORDER BY al.created_at DESC LIMIT :limit"
        params["limit"] = limit

        rows = execute_query(base_sql, params)
    except Exception as e:
        st.error(f"Could not load audit logs: {e}")
        return

    st.caption(f"Showing {len(rows)} log entries")

    if not rows:
        st.info("No audit logs found.")
        return

    for row in rows:
        log_id, action, entity_type, entity_id, status, ip, created, uname, role = row
        status_icon = "✅" if status == "success" else "❌"
        role_icon = {"patient":"🧑","doctor":"👨‍⚕️","admin":"🛡️"}.get(role or "","👤")

        col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
        with col_a:
            st.markdown(f"{status_icon} **{action}**")
        with col_b:
            st.caption(f"{role_icon} {uname}")
        with col_c:
            if entity_type:
                st.caption(f"Entity: {entity_type} #{entity_id or ''}")
        with col_d:
            st.caption(fmt_datetime(created))

        st.markdown("<hr style='margin:4px 0;border-color:#1E293B'>", unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────────
    try:
        import pandas as pd
        df = pd.DataFrame(
            rows,
            columns=["ID","Action","Entity Type","Entity ID","Status","IP","Created","User","Role"],
        )
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Export to CSV",
            data=csv,
            file_name="audit_logs.csv",
            mime="text/csv",
        )
    except ImportError:
        pass
