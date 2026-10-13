"""
Patient Profile - view and edit personal health profile.
"""
import streamlit as st
from datetime import date
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]

    section_header("👤 My Profile", "View and update your personal health information")

    try:
        row = execute_query(
            """SELECT p.date_of_birth, p.gender, p.blood_group, p.height_cm, p.weight_kg,
                      p.address, p.city, p.state, p.country, p.pincode, p.occupation,
                      p.marital_status, p.known_allergies, p.chronic_conditions,
                      p.current_medications, p.family_medical_history,
                      p.insurance_provider, p.insurance_id,
                      u.full_name, u.email, u.phone, u.preferred_language
               FROM patients p JOIN users u ON p.user_id=u.id
               WHERE p.id=:pid""",
            {"pid": pid},
        )
    except Exception as e:
        st.error(f"Could not load profile: {e}")
        return

    existing = row[0] if row else None

    tab_view, tab_edit = st.tabs(["👁️ View Profile", "✏️ Edit Profile"])

    with tab_view:
        if not existing:
            st.info("Profile not set up yet. Fill in the Edit tab.")
            return
        (dob, gender, bg, height, weight, address, city, state, country, pincode,
         occupation, marital, allergies, conditions, meds, fam_history,
         ins_provider, ins_id, fname, email, phone, pref_lang) = existing

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Name", fname or "—")
            st.metric("Date of Birth", str(dob) if dob else "—")
            st.metric("Gender", gender or "—")
        with c2:
            st.metric("Blood Group", bg or "—")
            st.metric("Height", f"{height} cm" if height else "—")
            st.metric("Weight", f"{weight} kg" if weight else "—")
        with c3:
            st.metric("Email", email or "—")
            st.metric("Phone", phone or "—")
            st.metric("Language", "Tamil" if pref_lang == "ta" else "English")

        if any([allergies, conditions, meds]):
            st.markdown("---")
            if allergies:
                st.markdown(f"**🚨 Known Allergies:** {allergies}")
            if conditions:
                st.markdown(f"**🏥 Chronic Conditions:** {conditions}")
            if meds:
                st.markdown(f"**💊 Current Medications:** {meds}")
            if fam_history:
                st.markdown(f"**👨‍👩‍👧 Family History:** {fam_history}")

        if ins_provider or ins_id:
            st.markdown("---")
            st.markdown(f"**🛡️ Insurance:** {ins_provider or '—'} — {ins_id or '—'}")

    with tab_edit:
        if existing:
            (dob, gender, bg, height, weight, address, city, state, country, pincode,
             occupation, marital, allergies, conditions, meds, fam_history,
             ins_provider, ins_id, fname, email, phone, pref_lang) = existing
        else:
            dob = gender = bg = height = weight = address = city = state = None
            country = "India"
            pincode = occupation = marital = allergies = conditions = meds = None
            fam_history = ins_provider = ins_id = None
            fname = user["name"]
            email = user["email"]
            phone = pref_lang = None

        with st.form("profile_form"):
            st.markdown("**Personal Information**")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_name = st.text_input("Full Name", value=fname or "")
                new_dob = st.date_input("Date of Birth", value=dob if dob else date(1990,1,1))
                new_gender = st.selectbox("Gender", ["","Male","Female","Other"],
                                          index=["","Male","Female","Other"].index(gender or ""))
            with c2:
                new_bg = st.selectbox("Blood Group", ["","A+","A-","B+","B-","AB+","AB-","O+","O-"],
                                      index=["","A+","A-","B+","B-","AB+","AB-","O+","O-"].index(bg or ""))
                new_height = st.number_input("Height (cm)", value=float(height) if height else 0.0, min_value=0.0)
                new_weight = st.number_input("Weight (kg)", value=float(weight) if weight else 0.0, min_value=0.0)
            with c3:
                new_phone = st.text_input("Phone", value=phone or "")
                new_lang = st.selectbox("Preferred Language", ["en","ta"],
                                        index=0 if (pref_lang or "en") == "en" else 1,
                                        format_func=lambda x: "English" if x=="en" else "Tamil")
                new_occupation = st.text_input("Occupation", value=occupation or "")

            st.markdown("**Address**")
            c1, c2 = st.columns(2)
            with c1:
                new_address = st.text_area("Address", value=address or "", height=80)
                new_city = st.text_input("City", value=city or "")
            with c2:
                new_state = st.text_input("State", value=state or "")
                new_country = st.text_input("Country", value=country or "India")
                new_pincode = st.text_input("Pincode", value=pincode or "")

            st.markdown("**Medical Information**")
            new_allergies = st.text_input("Known Allergies", value=allergies or "")
            new_conditions = st.text_input("Chronic Conditions", value=conditions or "")
            new_meds = st.text_area("Current Medications", value=meds or "", height=80)
            new_fam_history = st.text_area("Family Medical History", value=fam_history or "", height=80)

            st.markdown("**Insurance**")
            c1, c2 = st.columns(2)
            with c1:
                new_ins_provider = st.text_input("Insurance Provider", value=ins_provider or "")
            with c2:
                new_ins_id = st.text_input("Insurance ID", value=ins_id or "")

            submitted = st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True)

        if submitted:
            try:
                execute_write(
                    """UPDATE patients SET
                       date_of_birth=:dob, gender=:gender, blood_group=:bg,
                       height_cm=:height, weight_kg=:weight, address=:addr,
                       city=:city, state=:state, country=:country, pincode=:pincode,
                       occupation=:occ, known_allergies=:allergy,
                       chronic_conditions=:cond, current_medications=:meds,
                       family_medical_history=:famhist,
                       insurance_provider=:ins, insurance_id=:insid,
                       updated_at=NOW()
                       WHERE id=:pid""",
                    {"pid": pid, "dob": new_dob, "gender": new_gender, "bg": new_bg,
                     "height": new_height or None, "weight": new_weight or None,
                     "addr": new_address, "city": new_city, "state": new_state,
                     "country": new_country, "pincode": new_pincode, "occ": new_occupation,
                     "allergy": new_allergies, "cond": new_conditions, "meds": new_meds,
                     "famhist": new_fam_history, "ins": new_ins_provider, "insid": new_ins_id},
                )
                execute_write(
                    "UPDATE users SET full_name=:name, phone=:phone, preferred_language=:lang, updated_at=NOW() WHERE id=:uid",
                    {"name": new_name, "phone": new_phone, "lang": new_lang, "uid": user["id"]},
                )
                st.session_state["user_name"] = new_name
                st.session_state["language"] = new_lang
                st.success("✅ Profile updated successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save: {e}")
