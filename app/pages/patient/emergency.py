"""
Emergency - emergency contacts and first-aid guidance.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, emergency_alert


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]

    emergency_alert()
    section_header("🚨 Emergency", "Emergency contacts and quick first-aid guidance")

    tab_contacts, tab_add, tab_guide = st.tabs([
        "📞 Emergency Contacts", "➕ Add Contact", "🩹 First Aid Guide"
    ])

    with tab_contacts:
        try:
            contacts = execute_query(
                """SELECT id, name, relationship, phone, alternate_phone, is_primary
                   FROM emergency_contacts WHERE patient_id=:pid ORDER BY is_primary DESC, name""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(str(e))
            contacts = []

        # National emergency numbers always shown
        st.markdown("### 🇮🇳 National Emergency Numbers")
        ems = [("🚨 Emergency","112"),("🏥 Ambulance","108"),("🚒 Fire","101"),
               ("🚓 Police","100"),("👶 Child Helpline","1098"),("👩 Women Helpline","1091")]
        cols = st.columns(3)
        for i, (label, number) in enumerate(ems):
            with cols[i % 3]:
                st.markdown(f"**{label}:** `{number}`")

        st.markdown("---")
        st.markdown("### 👥 My Emergency Contacts")
        if not contacts:
            st.info("No emergency contacts saved. Add them in the 'Add Contact' tab.")
        else:
            for row in contacts:
                cid, name, rel, phone, alt_phone, is_primary = row
                icon = "⭐" if is_primary else "👤"
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"{icon} **{name}** — {rel or '—'}")
                    with c2:
                        st.markdown(f"📞 {phone}")
                        if alt_phone:
                            st.caption(f"Alt: {alt_phone}")
                    with c3:
                        if st.button("🗑️", key=f"del_ec_{cid}"):
                            try:
                                execute_write("DELETE FROM emergency_contacts WHERE id=:cid", {"cid": cid})
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    with tab_add:
        with st.form("emergency_contact_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Contact Name *")
                phone = st.text_input("Primary Phone *", placeholder="+91 98765 43210")
                is_primary = st.checkbox("Set as primary emergency contact")
            with c2:
                relationship = st.selectbox("Relationship", [
                    "Spouse","Parent","Child","Sibling","Friend","Doctor","Other"
                ])
                alt_phone = st.text_input("Alternate Phone (optional)")
                email = st.text_input("Email (optional)")

            address = st.text_area("Address (optional)", height=60)
            submitted = st.form_submit_button("💾 Save Contact", type="primary", use_container_width=True)

        if submitted:
            if not name.strip() or not phone.strip():
                st.error("Name and phone number are required.")
            else:
                try:
                    if is_primary:
                        execute_write(
                            "UPDATE emergency_contacts SET is_primary=FALSE WHERE patient_id=:pid",
                            {"pid": pid},
                        )
                    execute_write(
                        """INSERT INTO emergency_contacts
                           (patient_id, name, relationship, phone, alternate_phone,
                            email, address, is_primary, created_at)
                           VALUES (:pid,:name,:rel,:phone,:alt,:email,:addr,:primary,NOW())""",
                        {"pid": pid, "name": name, "rel": relationship,
                         "phone": phone, "alt": alt_phone, "email": email,
                         "addr": address, "primary": is_primary},
                    )
                    st.success(f"✅ {name} saved as emergency contact.")
                except Exception as e:
                    st.error(str(e))

    with tab_guide:
        st.markdown("### 🩹 Basic First Aid Reminders")
        st.warning("These are general guidelines only. Always call emergency services first.")
        guides = {
            "❤️ Cardiac Arrest (CPR)": """
1. Call **112** immediately
2. Begin chest compressions — 30 hard, fast pushes in the centre of the chest
3. Give 2 rescue breaths if trained
4. Continue until help arrives or AED is available
5. Use AED (defibrillator) if available — follow voice instructions
""",
            "🩸 Severe Bleeding": """
1. Call **108** (ambulance)
2. Apply firm, direct pressure with a clean cloth
3. Do not remove the cloth — add more on top if soaked
4. Elevate the injured area above the heart if possible
5. Keep the person still and calm
""",
            "🔥 Burns": """
1. Remove from heat source safely
2. Cool the burn with cool (NOT cold/ice) water for 10-20 minutes
3. Do not apply butter, toothpaste, or ice
4. Cover loosely with a clean bandage
5. Seek medical attention for large or deep burns
""",
            "🫁 Choking": """
1. Ask "Are you choking?" — if they cannot speak, act immediately
2. Give 5 firm back blows between shoulder blades
3. If unsuccessful, give 5 abdominal thrusts (Heimlich manoeuvre)
4. Alternate back blows and abdominal thrusts
5. Call **112** if unconscious
""",
            "🧠 Stroke (FAST)": """
**F**ace — Is one side drooping?
**A**rms — Can they raise both arms?
**S**peech — Is it slurred or strange?
**T**ime — Call **112** immediately if any sign is present

Do NOT give food or water. Keep them calm and lying down.
""",
        }
        for title, content in guides.items():
            with st.expander(title):
                st.markdown(content)
