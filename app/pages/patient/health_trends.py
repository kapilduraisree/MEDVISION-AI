"""
Health Trends - visualise lab values and health metrics over time.
"""
import streamlit as st
from app.core.auth import require_auth
from app.core.database import execute_query
from app.core.utils import section_header, ai_disclaimer

try:
    import pandas as pd
    import plotly.express as px
    PLOT_OK = True
except ImportError:
    PLOT_OK = False


def show():
    user = require_auth(["patient"])
    pid = user["patient_id"]
    lang = user["language"]

    section_header("📈 Health Trends", "Track your lab values and metrics over time")
    ai_disclaimer(lang)

    if not PLOT_OK:
        st.warning("Install pandas and plotly for charts: `pip install pandas plotly`")
        return

    # ── Health Metrics ────────────────────────────────────────────────────────
    st.markdown("### 📊 Health Metrics")
    try:
        metric_names = execute_query(
            "SELECT DISTINCT metric_name FROM health_metrics WHERE patient_id=:pid ORDER BY metric_name",
            {"pid": pid},
        )
    except Exception as e:
        st.error(f"Could not load metrics: {e}")
        metric_names = []

    if metric_names:
        selected_metric = st.selectbox(
            "Select metric to chart",
            [r[0] for r in metric_names],
        )
        try:
            rows = execute_query(
                """SELECT recorded_date, value, unit, notes
                   FROM health_metrics
                   WHERE patient_id=:pid AND metric_name=:name
                   ORDER BY recorded_date""",
                {"pid": pid, "name": selected_metric},
            )
        except Exception as e:
            rows = []
            st.error(str(e))

        if rows:
            df = pd.DataFrame(rows, columns=["Date","Value","Unit","Notes"])
            df["Date"] = pd.to_datetime(df["Date"])
            unit = df["Unit"].iloc[0] if not df["Unit"].isna().all() else ""
            fig = px.line(
                df, x="Date", y="Value",
                title=f"{selected_metric} over time",
                labels={"Value": f"{selected_metric} ({unit})"},
                markers=True,
                template="plotly_dark",
            )
            fig.update_layout(
                plot_bgcolor="#0F172A",
                paper_bgcolor="#0F172A",
                font_color="#F1F5F9",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df[["Date","Value","Unit"]].sort_values("Date", ascending=False), use_container_width=True)
    else:
        st.info("No health metrics recorded yet.")

    # ── Log new metric ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ➕ Log New Reading")
    with st.form("metric_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_name = st.selectbox("Metric", [
                "Blood Pressure (Systolic)","Blood Pressure (Diastolic)",
                "Blood Sugar (Fasting)","Blood Sugar (Post-meal)",
                "HbA1c","Weight (kg)","BMI","Heart Rate",
                "SpO2 (Oxygen)","Temperature","Cholesterol (Total)",
                "Hemoglobin","Custom",
            ])
        with c2:
            custom_name = st.text_input("Custom metric name (if selected above)")
            value = st.number_input("Value", min_value=0.0, format="%.2f")
        with c3:
            unit = st.text_input("Unit", placeholder="mg/dL, kg, bpm…")
            from datetime import date
            recorded_date = st.date_input("Date", value=date.today())

        notes = st.text_input("Notes (optional)")
        log_submit = st.form_submit_button("📥 Save Reading", type="primary")

    if log_submit:
        name = custom_name.strip() if metric_name == "Custom" and custom_name.strip() else metric_name
        if not name:
            st.error("Please specify a metric name.")
        elif value <= 0:
            st.error("Please enter a valid value.")
        else:
            try:
                execute_query(
                    """INSERT INTO health_metrics
                       (patient_id, metric_name, value, unit, recorded_date, source, notes, created_at)
                       VALUES (:pid,:name,:val,:unit,:rd,'manual',:notes,NOW())""",
                    {"pid": pid, "name": name, "val": value,
                     "unit": unit, "rd": recorded_date, "notes": notes},
                )
                st.success(f"✅ Logged {name}: {value} {unit}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to log reading: {e}")

    # ── Report value trends ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🧪 Lab Report Value Trends")
    try:
        test_names = execute_query(
            """SELECT DISTINCT rv.test_name
               FROM report_values rv
               JOIN medical_reports mr ON rv.report_id = mr.id
               WHERE mr.patient_id=:pid
               ORDER BY rv.test_name""",
            {"pid": pid},
        )
    except Exception as e:
        test_names = []

    if test_names:
        selected_test = st.selectbox("Select test", [r[0] for r in test_names], key="test_trend")
        try:
            rows = execute_query(
                """SELECT mr.report_date, rv.result, rv.unit, rv.status
                   FROM report_values rv
                   JOIN medical_reports mr ON rv.report_id = mr.id
                   WHERE mr.patient_id=:pid AND rv.test_name=:tn
                   ORDER BY mr.report_date""",
                {"pid": pid, "tn": selected_test},
            )
        except Exception:
            rows = []

        if rows:
            df2 = pd.DataFrame(rows, columns=["Date","Result","Unit","Status"])
            df2["Date"] = pd.to_datetime(df2["Date"])
            df2["Result"] = pd.to_numeric(df2["Result"], errors="coerce")
            df2 = df2.dropna(subset=["Result"])
            if not df2.empty:
                color_map = {"normal":"#10B981","attention":"#F59E0B","abnormal":"#EF4444","unknown":"#64748B"}
                df2["Color"] = df2["Status"].map(color_map).fillna("#64748B")
                fig2 = px.line(df2, x="Date", y="Result",
                               title=f"{selected_test} trend",
                               markers=True, template="plotly_dark",
                               color_discrete_sequence=["#0EA5E9"])
                fig2.update_layout(plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9")
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Upload reports to see lab value trends here.")
