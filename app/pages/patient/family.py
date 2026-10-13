"""
Family Profiles - manage health records for family members.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, fmt_date


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]

    section_header("👨‍👩‍👧‍👦 Family Profiles", "Manage health records for your family members")

    tab_add, tab_view = st.tabs(["➕ Add Member", "👥 Family Members"])

    with tab_add:
        with st.form("family_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *")
                relationship = st.selectbox("Relationship", [
                    "Spouse","Parent","Child","Sibling","Grandparent","Other"
                ])
                dob = st.date_input("Date of Birth")
            with c2:
                gender = st.selectbox("Gender", ["Male","Female","Other"])
                blood_group = st.selectbox("Blood Group", ["","A+","A-","B+","B-","AB+","AB-","O+","O-"])
                allergies = st.text_input("Known Allergies", placeholder="e.g. Penicillin, dust")

            conditions = st.text_input("Chronic Conditions", placeholder="e.g. Diabetes, Hypertension")
            medications = st.text_input("Current Medications", placeholder="e.g. Metformin 500mg")
            submitted = st.form_submit_button("➕ Add Family Member", type="primary", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                try:
                    execute_write(
                        """INSERT INTO family_members
                           (patient_id, name, relationship, date_of_birth, gender,
                            blood_group, known_allergies, chronic_conditions,
                            current_medications, is_active, created_at)
                           VALUES (:pid,:name,:rel,:dob,:gender,:bg,:allergy,:cond,:meds,TRUE,NOW())""",
                        {"pid": pid, "name": name.strip(), "rel": relationship,
                         "dob": dob, "gender": gender, "bg": blood_group,
                         "allergy": allergies, "cond": conditions, "meds": medications},
                    )
                    st.success(f"✅ {name} added to your family profile.")
                except Exception as e:
                    st.error(f"Failed to add member: {e}")

    with tab_view:
        try:
            members = execute_query(
                """SELECT id, name, relationship, date_of_birth, gender,
                          blood_group, chronic_conditions, known_allergies, current_medications
                   FROM family_members WHERE patient_id=:pid AND is_active=TRUE
                   ORDER BY name""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(str(e))
            return

        if not members:
            st.info("No family members added yet.")
            return

        for member in members:
            fid, name, rel, dob, gender, bg, conditions, allergies, meds = member
            icon = {"Spouse":"💑","Parent":"👴","Child":"👶","Sibling":"👫"}.get(rel,"👤")
            with st.expander(f"{icon} {name} — {rel}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("DOB", fmt_date(dob) if dob else "—")
                with c2:
                    st.metric("Gender", gender or "—")
                with c3:
                    st.metric("Blood Group", bg or "—")

                if conditions:
                    st.markdown(f"**Conditions:** {conditions}")
                if allergies:
                    st.markdown(f"**Allergies:** {allergies}")
                if meds:
                    st.markdown(f"**Medications:** {meds}")

                if st.button(f"🗑️ Remove {name}", key=f"del_fam_{fid}"):
                    try:
                        execute_write(
                            "UPDATE family_members SET is_active=FALSE WHERE id=:fid",
                            {"fid": fid}
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
