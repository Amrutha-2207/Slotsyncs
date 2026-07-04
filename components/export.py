"""Export tab — PDF download of the finalised timetable."""
from __future__ import annotations
import streamlit as st
from datetime import datetime

from utils.export import export_timetable_pdf


def render_export() -> None:
    st.markdown(
        '<div class="ss-section-title"><h2>Export</h2>'
        '<span class="aside">STEP 06 · SHARE</span></div>',
        unsafe_allow_html=True,
    )

    selected = st.session_state.selected_courses
    if not selected:
        st.markdown(
            '<div class="ss-panel" style="text-align:center;color:var(--muted);">'
            'Nothing to export yet — build your timetable first.</div>',
            unsafe_allow_html=True,
        )
        return

    with st.container():
        st.markdown('<div class="ss-panel">', unsafe_allow_html=True)
        name = st.text_input("Your name (optional)",
                             key="export_name",
                             placeholder="Appears at the top of the PDF")
        try:
            pdf_bytes = export_timetable_pdf(selected, student_name=name or "")
            filename = f"SlotSync_Timetable_{datetime.now():%Y%m%d}.pdf"
            st.download_button(
                "⬇  Download PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key="download-pdf-btn",
            )
            st.markdown(
                '<div class="ss-mono ss-mute" style="font-size:11px;letter-spacing:.12em;margin-top:10px;">'
                'PDF · LANDSCAPE A4 · INCLUDES COURSE LIST</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:  # noqa
            st.error(f"Couldn't render PDF: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
