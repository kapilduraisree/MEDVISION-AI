"""
Medical Locker - secure storage for medical documents.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, save_uploaded_file, fmt_date


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]

    section_header("🔒 Medical Locker", "Securely store and access all your medical documents")

    tab_upload, tab_docs = st.tabs(["📤 Upload Document", "📁 My Documents"])

    with tab_upload:
        with st.form("locker_form"):
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox("Category", [
                    "Blood Report","Scan / Imaging","Prescription","Insurance",
                    "Discharge Summary","Vaccination Record","Doctor Notes","Other",
                ])
                title = st.text_input("Document Title *", placeholder="e.g. CBC Report Jan 2026")
            with c2:
                doc_date = st.date_input("Document Date")
                tags = st.text_input("Tags (comma-separated)", placeholder="diabetes, kidney, annual")

            description = st.text_area("Description (optional)", height=80)
            uploaded = st.file_uploader(
                "Upload File",
                type=["jpg","jpeg","png","pdf","docx","doc"],
            )
            submitted = st.form_submit_button("📥 Upload to Locker", type="primary", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Document title is required.")
            elif not uploaded:
                st.error("Please select a file to upload.")
            else:
                file_path = save_uploaded_file(uploaded, "locker") or ""
                file_size = len(uploaded.getvalue()) // 1024
                try:
                    execute_write(
                        """INSERT INTO documents
                           (patient_id, category, title, description, file_path,
                            original_filename, file_type, file_size_kb, document_date,
                            tags, is_deleted, created_at)
                           VALUES (:pid,:cat,:title,:desc,:fp,:fn,:ftype,:fsize,:dd,:tags,FALSE,NOW())""",
                        {"pid": pid, "cat": category, "title": title.strip(),
                         "desc": description, "fp": file_path, "fn": uploaded.name,
                         "ftype": uploaded.type, "fsize": file_size,
                         "dd": doc_date, "tags": tags},
                    )
                    st.success(f"✅ '{title}' uploaded to your Medical Locker.")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    with tab_docs:
        # Filter
        col_f1, col_f2 = st.columns([2, 3])
        with col_f1:
            filter_cat = st.selectbox("Filter by category", ["All","Blood Report","Scan / Imaging",
                "Prescription","Insurance","Discharge Summary","Vaccination Record","Doctor Notes","Other"])
        with col_f2:
            search_title = st.text_input("Search by title or tag", placeholder="Search…")

        try:
            if filter_cat != "All":
                rows = execute_query(
                    """SELECT id, category, title, original_filename, file_size_kb,
                              document_date, tags, created_at
                       FROM documents WHERE patient_id=:pid AND is_deleted=FALSE AND category=:cat
                       ORDER BY created_at DESC""",
                    {"pid": pid, "cat": filter_cat},
                )
            else:
                rows = execute_query(
                    """SELECT id, category, title, original_filename, file_size_kb,
                              document_date, tags, created_at
                       FROM documents WHERE patient_id=:pid AND is_deleted=FALSE
                       ORDER BY created_at DESC""",
                    {"pid": pid},
                )
        except Exception as e:
            st.error(str(e))
            return

        if search_title:
            rows = [r for r in rows if search_title.lower() in (r[2] or "").lower()
                    or search_title.lower() in (r[6] or "").lower()]

        if not rows:
            st.info("No documents found. Use the Upload tab to add files.")
            return

        st.caption(f"{len(rows)} document(s) found")
        for row in rows:
            did, cat, title, fname, fsize, doc_date, tags, created = row
            icon = {"Blood Report":"🩸","Scan / Imaging":"🔬","Prescription":"💊",
                    "Insurance":"📋","Discharge Summary":"🏥",
                    "Vaccination Record":"💉","Doctor Notes":"📝"}.get(cat,"📄")
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    st.markdown(f"{icon} **{title}**")
                    st.caption(f"{cat}  •  {fname or ''}  •  {fsize or '—'} KB")
                    if tags:
                        st.caption(f"🏷️ {tags}")
                with c2:
                    st.caption(f"Document date: {fmt_date(doc_date)}")
                    st.caption(f"Uploaded: {fmt_date(created)}")
                with c3:
                    if st.button("🗑️", key=f"del_doc_{did}", help="Delete document"):
                        try:
                            execute_write(
                                "UPDATE documents SET is_deleted=TRUE WHERE id=:did",
                                {"did": did},
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
