"""
Admin – Doctor Management
Verify, view and manage doctor profiles.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_date


def show():
    user = require_auth(["admin"])
    section_header("👨‍⚕️ Doctor Management", "View and verify all registered doctors")

    search = st.text_input("🔍 Search doctors", placeholder="Name, specialization, hospital…")
    verified_filter = st.selectbox("Verification Status", ["all","verified","unverified"])

    try:
        base_sql = """
            SELECT d.id, u.full_name, u.email, u.phone, u.is_active,
                   d.specialization, d.qualification, d.registration_number,
                   d.hospital_name, d.city, d.years_of_experience,
                   d.consultation_fee, d.is_verified, d.is_available, u.created_at
            FROM doctors d JOIN users u ON d.user_id=u.id WHERE 1=1
        """
        params = {}
        if verified_filter == "verified":
            base_sql += " AND d.is_verified=TRUE"
        elif verified_filter == "unverified":
            base_sql += " AND d.is_verified=FALSE"
        if search:
            base_sql += " AND (LOWER(u.full_name) LIKE :s OR LOWER(d.specialization) LIKE :s OR LOWER(d.hospital_name) LIKE :s)"
            params["s"] = f"%{search.lower()}%"
        base_sql += " ORDER BY u.full_name"
        doctors = execute_query(base_sql, params)
    except Exception as e:
        st.error(str(e))
        return

    st.caption(f"{len(doctors)} doctor(s) found")

    for doc in doctors:
        (did, name, email, phone, is_active, spec, qual, reg_no,
         hospital, city, exp, fee, is_verified, is_available, created) = doc

        verified_icon = "✅" if is_verified else "⏳"
        active_icon = "🟢" if is_active else "🔴"

        with st.expander(f"{verified_icon} {active_icon} Dr. {name}  —  {spec or 'General'}  —  {hospital or ''}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Specialization", spec or "—")
                st.metric("Experience", f"{exp or 0} yrs")
                st.caption(f"📧 {email}")
            with c2:
                st.metric("Hospital", (hospital or "—")[:30])
                st.metric("City", city or "—")
                st.metric("Fee", f"₹{fee or 0}")
            with c3:
                st.metric("Reg. No", reg_no or "—")
                st.metric("Verified", "Yes" if is_verified else "No")
                st.metric("Available", "Yes" if is_available else "No")

            if qual:
                st.caption(f"Qualification: {qual}")

            btn1, btn2, btn3 = st.columns(3)
            with btn1:
                if not is_verified:
                    if st.button("✅ Verify Doctor", key=f"vdoc2_{did}"):
                        try:
                            execute_write("UPDATE doctors SET is_verified=TRUE WHERE id=:did", {"did": did})
                            st.success(f"Dr. {name} verified.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
            with btn2:
                avail_label = "🔴 Set Unavailable" if is_available else "🟢 Set Available"
                if st.button(avail_label, key=f"avail_{did}"):
                    try:
                        execute_write("UPDATE doctors SET is_available=:v WHERE id=:did",
                                      {"v": not is_available, "did": did})
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            with btn3:
                active_label = "🔴 Deactivate" if is_active else "🟢 Activate"
                if st.button(active_label, key=f"dact_{did}"):
                    try:
                        execute_write(
                            "UPDATE users SET is_active=:v WHERE id=(SELECT user_id FROM doctors WHERE id=:did)",
                            {"v": not is_active, "did": did}
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
