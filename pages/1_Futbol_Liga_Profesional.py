
import streamlit as st
import pandas as pd

st.markdown("# 🇦🇷 Liga Profesional")

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

st.markdown("# 🇦🇷 Liga Profesional")
tabs = st.tabs(["Tabla", "Fixture", "Campeones", "Estadísticas", "Historia de Clubes", "Simuladores"])

with tabs[0]:
    st.subheader("Tabla (auto-actualizable)")
    tabla = compute_standings(matches, teams)

    # Mostrar logos oficiales en una columna HTML
    def logo_html(url): return f'<img src="{url}" height="24">'
    tabla_show = tabla.copy()
    tabla_show.insert(2, "Escudo", tabla_show["escudo_url"].apply(logo_html))
    tabla_show = tabla_show.drop(columns=["escudo_url"])
    st.write(tabla_show.to_html(escape=False, index=False), unsafe_allow_html=True)

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
