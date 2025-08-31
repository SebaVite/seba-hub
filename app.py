
import streamlit as st

st.set_page_config(page_title="Seba Hub", layout="wide")

st.markdown("# ⚽️📊 Seba Hub")
st.write("Datos buenos + simuladores. Hoy abrimos **Fútbol** (Mundo 1).")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### Fútbol")
    st.write("Tablas, fixture, historia y simuladores.")
    st.page_link("pages/1_Futbol_Liga_Profesional.py", label="Entrar →", icon="⚽")
with col2:
    st.markdown("### Videojuegos")
    st.caption("Próximamente: packs, drop rates, etc.")
with col3:
    st.markdown("### F1")
    st.caption("Próximamente: estrategias y comparador.")
with col4:
    st.markdown("### Seguridad / IAM")
    st.caption("Próximamente: riesgos gamificados.")
