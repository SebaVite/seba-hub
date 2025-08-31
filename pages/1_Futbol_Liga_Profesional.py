import streamlit as st
import pandas as pd
import base64, os
from pathlib import Path

# ── Config (debe ser la primera llamada st.*) ───────────────────────────────────
st.set_page_config(page_title="Liga Profesional", layout="wide")

# Botón para limpiar caché y recargar
if st.button("🔄 Refrescar datos"):
    st.cache_data.clear()
    st.rerun()

# ── Helpers de paths / imágenes ─────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # raíz del repo

def resolve_path(p: str) -> Path:
    """Convierte rutas relativas del repo a absoluta robusta."""
    pp = Path(p.strip()).as_posix().lstrip("/")  # normaliza y quita "/" inicial
    return BASE_DIR / pp

def local_img_to_data_uri(path: str) -> str:
    """Convierte un archivo local (PNG/JPG) a data URI."""
    full = resolve_path(path)
    with open(full, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    mime = "image/png" if full.suffix.lower()==".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"

def img_src(p: str) -> str:
    """
    Si p es URL (http/https) -> la devolvemos tal cual.
    Si p es ruta local -> devolvemos data URI embebida.
    """
    p = (p or "").strip()
    if p.startswith("http://") or p.startswith("https://"):
        return p
    try:
        return local_img_to_data_uri(p)
    except Exception as e:
        st.write("⚠️ No pude leer archivo local:", resolve_path(p), "| Error:", repr(e))
        return ""

# ── Datos ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    teams = pd.read_csv("data/teams.csv")
    matches = pd.read_csv("data/matches.csv")
    return teams, matches

def compute_standings(matches, teams):
    m = matches[matches["status"] == "finished"].copy()

    # registros local
    home = m[["home_id","home_goals","away_goals"]].rename(
        columns={"home_id":"team_id","home_goals":"gf","away_goals":"ga"}
    )
    # registros visitante
    away = m[["away_id","away_goals","home_goals"]].rename(
        columns={"away_id":"team_id","away_goals":"gf","home_goals":"ga"}
    )

    for df in (home, away):
        df["pj"] = 1
        df["pg"] = (df["gf"] > df["ga"]).astype(int)
        df["pe"] = (df["gf"] == df["ga"]).astype(int)
        df["pp"] = (df["gf"] < df["ga"]).astype(int)
        df["pts"] = df["pg"]*3 + df["pe"]

    rows = pd.concat([home, away], ignore_index=True)
    agg = rows.groupby("team_id", as_index=False).sum(numeric_only=True)
    agg["dg"] = agg["gf"] - agg["ga"]

    tabla = teams.merge(agg, left_on="id", right_on="team_id", how="left").fillna(0)
    for c in ["pj","pg","pe","pp","gf","ga","dg","pts"]:
        tabla[c] = tabla[c].astype(int)

    tabla = (
        tabla.sort_values(["pts","dg","gf","nombre"], ascending=[False, False, False, True])
             .reset_index(drop=True)
    )
    tabla.insert(0, "pos", tabla.index+1)
    return tabla[["pos","nombre","pj","pg","pe","pp","gf","ga","dg","pts","escudo_url"]]

teams, matches = load_data()

# ── Encabezado ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="display:flex; align-items:center; gap:12px;">
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Argentina.svg/32px-Flag_of_Argentina.svg.png" height="24">
      <h1 style="margin:0;">Liga Profesional</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ── Tabs ────────────────────────────────────────────────────────────────────────
tabs = st.tabs(["Tabla", "Fixture", "Campeones", "Estadísticas", "Historia de Clubes", "Simuladores"])

with tabs[0]:
    st.subheader("Tabla (auto-actualizable)")
    tabla = compute_standings(matches, teams).copy()

    # Escudos embebidos (funciona con URL o ruta local)
    tabla["Escudo"] = tabla["escudo_url"].astype(str).apply(
        lambda p: f'<img src="{img_src(p)}" height="24">' if p else "—"
    )

    cols = ["pos","nombre","Escudo","pj","pg","pe","pp","gf","ga","dg","pts"]
    st.markdown(tabla[cols].to_html(escape=False, index=False), unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Fixture")
    st.dataframe(matches, use_container_width=True)

with tabs[2]:
    st.subheader("Campeones (placeholder)")
    st.info("Acá va el historial real por temporada.")

with tabs[3]:
    st.subheader("Estadísticas (placeholder)")
    st.info("Goleadores, asistencias, tarjetas…")

with tabs[4]:
    st.subheader("Historia de Clubes")
    equipo = st.selectbox("Elegí club", teams["nombre"].tolist())
    row = teams[teams["nombre"] == equipo].iloc[0]
    st.markdown(f"### {row['nombre']}")
    # Mostrar escudo del club (local o URL)
    st.markdown(f'<img src="{img_src(row["escudo_url"])}" height="80">', unsafe_allow_html=True)
    st.info("Acá va palmarés, ídolos, campañas históricas, etc.")

with tabs[5]:
    st.subheader("Simuladores")
    st.info("Pronto: ¿qué pasa si cambia un resultado? Prob. de título/descenso, etc.")
