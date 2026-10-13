"""
Pharmacy Bills - scan and track pharmacy expenses.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query, execute_write
from app.core.utils import section_header, save_uploaded_file, fmt_date
from app.services.ai.ocr_service import extract_text_from_bytes


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]

    section_header("🧾 Pharmacy Bills", "Scan and track your medicine expenses")

    tab_upload, tab_history = st.tabs(["📤 Upload Bill", "📋 Bill History"])

    with tab_upload:
        with st.form("bill_form"):
            c1, c2 = st.columns(2)
            with c1:
                pharmacy_name = st.text_input("Pharmacy Name", placeholder="e.g. Apollo Pharmacy")
                bill_date = st.date_input("Bill Date")
            with c2:
                total_amount = st.number_input("Total Amount (₹)", min_value=0.0, format="%.2f")
                notes = st.text_input("Notes (optional)")

            uploaded = st.file_uploader("Upload Bill Image or PDF", type=["jpg","jpeg","png","pdf"])
            submitted = st.form_submit_button("📥 Save Bill", type="primary", use_container_width=True)

        if submitted:
            file_path = ""
            ocr_text = ""
            items_extracted = []

            if uploaded:
                file_path = save_uploaded_file(uploaded, "pharmacy_bills") or ""
                with st.spinner("Extracting bill details…"):
                    file_bytes = uploaded.read()
                    ocr = extract_text_from_bytes(file_bytes, uploaded.name)
                    ocr_text = ocr.get("text","")
                    items_extracted = _parse_bill_items(ocr_text)

            try:
                execute_write(
                    """INSERT INTO pharmacy_bills
                       (patient_id, file_path, original_filename, pharmacy_name,
                        bill_date, total_amount, ocr_raw_text, notes, created_at)
                       VALUES (:pid,:fp,:fn,:pname,:bd,:total,:ocr,:notes,NOW())""",
                    {"pid": pid, "fp": file_path,
                     "fn": uploaded.name if uploaded else "",
                     "pname": pharmacy_name, "bd": bill_date,
                     "total": total_amount, "ocr": ocr_text, "notes": notes},
                )

                if items_extracted:
                    rows = execute_query(
                        "SELECT id FROM pharmacy_bills WHERE patient_id=:pid ORDER BY created_at DESC LIMIT 1",
                        {"pid": pid}
                    )
                    bill_id = rows[0][0] if rows else None
                    if bill_id:
                        for item in items_extracted:
                            execute_write(
                                """INSERT INTO pharmacy_bill_items
                                   (bill_id, medicine_name, quantity, unit_price, total_price, created_at)
                                   VALUES (:bid,:name,:qty,:up,:tp,NOW())""",
                                {"bid": bill_id, "name": item.get("name",""),
                                 "qty": item.get("quantity",""), "up": item.get("unit_price",0),
                                 "tp": item.get("total_price",0)},
                            )

                st.success("✅ Bill saved successfully.")
                if items_extracted:
                    st.markdown("### 💊 Extracted Items")
                    for item in items_extracted:
                        st.markdown(f"• **{item.get('name','')}** — Qty: {item.get('quantity','—')} — ₹{item.get('total_price','—')}")

            except Exception as e:
                st.error(f"Failed to save bill: {e}")

    with tab_history:
        try:
            rows = execute_query(
                """SELECT id, pharmacy_name, bill_date, total_amount, notes, created_at
                   FROM pharmacy_bills WHERE patient_id=:pid ORDER BY bill_date DESC""",
                {"pid": pid},
            )
        except Exception as e:
            st.error(str(e))
            return

        if not rows:
            st.info("No pharmacy bills uploaded yet.")
            return

        # Total spend
        try:
            total = sum((r[3] or 0) for r in rows)
            st.metric("💰 Total Pharmacy Spend", f"₹{total:,.2f}")
        except Exception:
            pass

        st.markdown("---")
        for row in rows:
            bid, pname, bdate, total_amt, notes, created = row
            with st.expander(f"🧾 {pname or 'Pharmacy'} — {fmt_date(bdate)} — ₹{total_amt or 0:,.2f}"):
                try:
                    items = execute_query(
                        "SELECT medicine_name, quantity, unit_price, total_price FROM pharmacy_bill_items WHERE bill_id=:bid",
                        {"bid": bid}
                    )
                    if items:
                        for item in items:
                            st.markdown(f"• **{item[0]}** — Qty: {item[1]} — ₹{item[3] or '—'}")
                    elif notes:
                        st.write(notes)
                except Exception:
                    pass


def _parse_bill_items(text: str) -> list:
    """Very basic item extractor from pharmacy bill OCR text."""
    import re
    items = []
    lines = text.strip().split("\n")
    price_pattern = re.compile(r"(\d+(?:\.\d{2})?)")
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if re.search(r"\d+\.\d{2}", line):
            prices = price_pattern.findall(line)
            items.append({
                "name": re.sub(r"[\d.]+", "", line).strip()[:80],
                "quantity": "1",
                "unit_price": float(prices[0]) if prices else 0,
                "total_price": float(prices[-1]) if prices else 0,
            })
    return items[:20]
