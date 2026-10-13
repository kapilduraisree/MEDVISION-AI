"""
Admin – User Management
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_datetime


def show():
    user = require_auth(["admin"])
    section_header("👥 User Management", "View, search, and manage all system users")

    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search by name or email", placeholder="Search…")
    with col2:
        role_filter = st.selectbox("Role", ["all","patient","doctor","admin"])
    with col3:
        status_filter = st.selectbox("Status", ["all","active","inactive"])

    try:
        base_sql = """SELECT id, full_name, email, phone, role, is_active, is_verified, created_at, last_login
                      FROM users WHERE 1=1"""
        params = {}
        if role_filter != "all":
            base_sql += " AND role=:role"
            params["role"] = role_filter
        if status_filter == "active":
            base_sql += " AND is_active=TRUE"
        elif status_filter == "inactive":
            base_sql += " AND is_active=FALSE"
        if search:
            base_sql += " AND (LOWER(full_name) LIKE :search OR LOWER(email) LIKE :search)"
            params["search"] = f"%{search.lower()}%"
        base_sql += " ORDER BY created_at DESC"
        rows = execute_query(base_sql, params)
    except Exception as e:
        st.error(f"Could not load users: {e}")
        return

    st.caption(f"{len(rows)} user(s) found")

    for row in rows:
        uid, name, email, phone, role, is_active, is_verified, created, last_login = row
        status_icon = "🟢" if is_active else "🔴"
        role_icon = {"patient":"🧑","doctor":"👨‍⚕️","admin":"🛡️"}.get(role,"👤")

        with st.expander(f"{status_icon} {role_icon} {name}  —  {email}  —  {role.capitalize()}"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Role", role.capitalize())
                st.metric("Status", "Active" if is_active else "Inactive")
            with c2:
                st.metric("Verified", "Yes" if is_verified else "No")
                if phone:
                    st.metric("Phone", phone)
            with c3:
                st.caption(f"Joined: {fmt_datetime(created)}")
                st.caption(f"Last login: {fmt_datetime(last_login) if last_login else 'Never'}")
            with c4:
                action_label = "🔴 Deactivate" if is_active else "🟢 Activate"
                if st.button(action_label, key=f"toggle_{uid}"):
                    try:
                        execute_write(
                            "UPDATE users SET is_active=:active WHERE id=:uid",
                            {"active": not is_active, "uid": uid},
                        )
                        st.success("User status updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

                if not is_verified:
                    if st.button("✅ Verify", key=f"verify_{uid}"):
                        try:
                            execute_write(
                                "UPDATE users SET is_verified=TRUE WHERE id=:uid",
                                {"uid": uid},
                            )
                            st.success("User verified.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ── Doctor verification section ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 👨‍⚕️ Pending Doctor Verifications")
    try:
        unverified_docs = execute_query(
            """SELECT d.id, u.full_name, u.email, d.specialization,
                      d.registration_number, d.hospital_name, d.qualification
               FROM doctors d JOIN users u ON d.user_id=u.id
               WHERE d.is_verified=FALSE AND u.is_active=TRUE
               ORDER BY u.created_at DESC""",
            {},
        )
    except Exception as e:
        unverified_docs = []

    if not unverified_docs:
        st.info("No pending doctor verifications.")
    else:
        for doc in unverified_docs:
            did, dname, demail, spec, reg_no, hospital, qual = doc
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 3, 1])
                with c1:
                    st.markdown(f"**Dr. {dname}** — {spec or 'N/A'}")
                    st.caption(f"Reg: {reg_no or '—'}  •  {hospital or '—'}")
                with c2:
                    st.caption(f"📧 {demail}")
                    if qual:
                        st.caption(f"Qualification: {qual[:60]}")
                with c3:
                    if st.button("✅ Verify Doctor", key=f"vdoc_{did}"):
                        try:
                            execute_write(
                                "UPDATE doctors SET is_verified=TRUE WHERE id=:did",
                                {"did": did},
                            )
                            execute_write(
                                "UPDATE users SET is_verified=TRUE WHERE id=(SELECT user_id FROM doctors WHERE id=:did)",
                                {"did": did},
                            )
                            st.success(f"Dr. {dname} verified.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
