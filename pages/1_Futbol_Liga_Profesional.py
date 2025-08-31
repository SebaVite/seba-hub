
import streamlit as st
import pandas as pd
import base64, os
from pathlib import Path

import base64, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # raíz del repo

def resolve_path(p: str) -> Path:
    pp = Path(p.strip()).as_posix().lstrip("/")  # normaliza
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
st.set_page_config(page_title="Liga Profesional", layout="wide")

@st.cache_data
def load_data():
    teams = pd.read_csv("data/teams.csv")
    matches = pd.read_csv("data/matches.csv")
    return teams, matches

def compute_standings(matches, teams):
    m = matches[matches["status"]=="finished"].copy()

    # registros local
    home = m[["home_id","home_goals","away_goals"]].rename(
        columns={"home_id":"team_id","home_goals":"gf","away_goals":"ga"}
    )
    # registros visitante
    away = m[["away_id","away_goals","home_goals"]].rename(
        columns={"away_id":"team_id","away_goals":"gf","home_goals":"ga"}
    )

    for df in (home, away):
        df["pj"]=1
        df["pg"]=(df["gf"]>df["ga"]).astype(int)
        df["pe"]=(df["gf"]==df["ga"]).astype(int)
        df["pp"]=(df["gf"]<df["ga"]).astype(int)
        df["pts"]=df["pg"]*3 + df["pe"]

    rows = pd.concat([home,away], ignore_index=True)
    agg = rows.groupby("team_id", as_index=False).sum(numeric_only=True)
    agg["dg"]=agg["gf"]-agg["ga"]

    tabla = teams.merge(agg, left_on="id", right_on="team_id", how="left").fillna(0)
    for c in ["pj","pg","pe","pp","gf","ga","dg","pts"]:
        tabla[c]=tabla[c].astype(int)
    tabla = tabla.sort_values(["pts","dg","gf","nombre"], ascending=[False,False,False,True]).reset_index(drop=True)
    tabla.insert(0,"pos", tabla.index+1)
    return tabla[["pos","nombre","pj","pg","pe","pp","gf","ga","dg","pts","escudo_url"]]

teams, matches = load_data()

st.markdown(
    """
    <div style="display:flex; align-items:center; gap:12px;">
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Argentina.svg/32px-Flag_of_Argentina.svg.png" height="24">
      <h1 style="margin:0;">Liga Profesional</h1>
    </div>
    """,
    unsafe_allow_html=True
)


tabs = st.tabs(["Tabla", "Fixture", "Campeones", "Estadísticas", "Historia de Clubes", "Simuladores"])

with tabs[0]:
    st.subheader("Tabla (auto-actualizable)")

    # 1) Cargar tabla base
    tabla = compute_standings(matches, teams).copy()  # debe tener 'escudo_url' con rutas tipo assets/logos/river.png

    # --- DEBUG mínimo y vista previa de escudos (para confirmar que se leen) ---
    st.caption("Vista previa de escudos (debug rápido)")
    c1, c2, c3, c4 = st.columns(4)
    try:
        c1.image(resolve_path("assets/logos/river.png"), width=48, caption="river.png")
    except Exception as e:
        c1.write(f"river.png ❌ {e}")
    try:
        c2.image(resolve_path("assets/logos/boca.png"), width=48, caption="boca.png")
    except Exception as e:
        c2.write(f"boca.png ❌ {e}")
    try:
        c3.image(resolve_path("assets/logos/independiente.png"), width=48, caption="independiente.png")
    except Exception as e:
        c3.write(f"independiente.png ❌ {e}")
    try:
        c4.image(resolve_path("assets/logos/racing.png"), width=48, caption="racing.png")
    except Exception as e:
        c4.write(f"racing.png ❌ {e}")

    st.divider()

    # 2) Convertir cada ruta en <img src="..."> (si es http la usa tal cual, si es local la embebe en base64)
    tabla["Escudo"] = tabla["escudo_url"].astype(str).apply(
        lambda p: f'<img src="{img_src(p)}" height="24">' if p else "—"
    )

    # 3) Renderizar tabla con HTML (permite imágenes)
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
    row = teams[teams["nombre"]==equipo].iloc[0]
    st.markdown(f"### {row['nombre']}")
    st.image(row["escudo_url"], width=80)
    st.info("Acá va palmarés, ídolos, campañas históricas, etc.")

with tabs[5]:
    st.subheader("Simuladores")
    st.info("Pronto: ¿qué pasa si cambia un resultado? Prob. de título/descenso, etc.")
