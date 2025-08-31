
import streamlit as st
import pandas as pd
import base64, os

def img_to_data_uri(path: str) -> str:
    """Lee un PNG/JPG local y devuelve un data URI para <img src="...">"""
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        return f"data:{mime};base64,{b64}"
    except Exception:
        return ""  # si falta el archivo, queda vacío


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
    tabla = compute_standings(matches, teams).copy()

    # Embebemos los escudos como data URI (no dependemos de URLs externas)
    tabla["Escudo"] = tabla["escudo_url"].astype(str).apply(
        lambda p: f'<img src="{img_to_data_uri(p)}" height="24">' if p else ""
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
    row = teams[teams["nombre"]==equipo].iloc[0]
    st.markdown(f"### {row['nombre']}")
    st.image(row["escudo_url"], width=80)
    st.info("Acá va palmarés, ídolos, campañas históricas, etc.")

with tabs[5]:
    st.subheader("Simuladores")
    st.info("Pronto: ¿qué pasa si cambia un resultado? Prob. de título/descenso, etc.")
