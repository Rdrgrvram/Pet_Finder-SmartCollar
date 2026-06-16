# ════════════════════════════════════════════════════════════════
#  PetFinder — Dashboard Analytics (FIXED FINAL VERSION)
# ════════════════════════════════════════════════════════════════

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="PetFinder Analytics",
    page_icon="🐾",
    layout="wide"
)

SUPABASE_URL = "https://kjuoamogxpplpyaseeat.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqdW9hbW9neHBwbHB5YXNlZWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTU1NDUsImV4cCI6MjA5MjM3MTU0NX0.ty8SNcnELPCKk43qoRJft4-8IVQz6GrSouoX4T188CQ"
TABLA = "lecturas_collar"


# ════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════

def autenticar(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    r = requests.post(
        url,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        },
        json={
            "email": email,
            "password": password
        },
        timeout=10
    )

    if r.status_code == 200:
        return r.json()["access_token"]

    st.error(r.text)
    return None


# ════════════════════════════════════════════════════════
# HEADERS
# ════════════════════════════════════════════════════════

def headers(token):
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {token}"
    }


# ════════════════════════════════════════════════════════
# DATA
# ════════════════════════════════════════════════════════

def obtener_datos(token, limite=100):

    url = (
        f"{SUPABASE_URL}/rest/v1/{TABLA}"
        f"?select=*&=timestamp.desc&limit={limite}"
    )

    r = requests.get(url, headers=headers(token), timeout=10)

    if r.status_code != 200:
        st.error(r.text)
        return []

    return r.json()


def to_df(data):
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # 🔥 FIX CLAVE: tu DB usa timestamp
    if "timestamp" not in df.columns:
        st.error("No existe columna 'timestamp' en la base de datos")
        return pd.DataFrame()

    df["created_at"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if "temperatura" in df.columns:
        df["temperatura"] = pd.to_numeric(df["temperatura"], errors="coerce")

    df = df.sort_values("created_at")

    return df


# ════════════════════════════════════════════════════════
# MÉTRICAS
# ════════════════════════════════════════════════════════

def metricas(df):

    if df.empty:
        return

    ultima = df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📊 Registros", len(df))
    c2.metric("🏃 Movimientos", int(df["movimiento"].sum()))

    temp = ultima.get("temperatura")
    c3.metric("🌡️ Temperatura", f"{temp:.1f}°C" if pd.notna(temp) else "—")

    gps = pd.notna(ultima.get("latitud")) and pd.notna(ultima.get("longitud"))
    c4.metric("📡 GPS", "OK" if gps else "—")


# ════════════════════════════════════════════════════════
# GRÁFICOS
# ════════════════════════════════════════════════════════

def grafico_temperatura(df):
    return px.line(
        df,
        x="created_at",
        y="temperatura",
        title="🌡️ Temperatura"
    )


def grafico_movimiento(df):
    df = df.copy()
    df["mov"] = df["movimiento"].astype(int)

    return px.bar(
        df,
        x="created_at",
        y="mov",
        title="🏃 Movimiento"
    )


def grafico_mapa(df):

    gps = df.dropna(subset=["latitud", "longitud"])

    if gps.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sin GPS", x=0.5, y=0.5)
        return fig

    fig = px.scatter_mapbox(
        gps,
        lat="latitud",
        lon="longitud",
        zoom=14,
        mapbox_style="open-street-map",
        title="📍 GPS"
    )

    ultimo = gps.iloc[-1]

    fig.add_trace(go.Scattermapbox(
        lat=[ultimo["latitud"]],
        lon=[ultimo["longitud"]],
        marker=dict(size=15, color="red")
    ))

    return fig


# ════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════

def login():

    st.title("🐾 PetFinder Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Entrar"):

        token = autenticar(email, password)

        if token:
            st.session_state["token"] = token
            st.rerun()
        else:
            st.error("Login incorrecto")


# ════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════

def dashboard(token):

    st.title("🐾 PetFinder Analytics")

    data = obtener_datos(token, 100)
    df = to_df(data)

    if df.empty:
        st.warning("No hay datos aún (verifica ESP32 o RLS)")
        return

    metricas(df)
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(grafico_temperatura(df), use_container_width=True)

    with col2:
        st.plotly_chart(grafico_movimiento(df), use_container_width=True)

    st.plotly_chart(grafico_mapa(df), use_container_width=True)

    st.subheader("📋 Historial")

    cols = ["created_at", "temperatura", "movimiento", "latitud", "longitud"]
    cols = [c for c in cols if c in df.columns]

    st.dataframe(
        df[cols].sort_values("created_at", ascending=False),
        use_container_width=True
    )


# ════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════

def main():

    if "token" not in st.session_state:
        login()
    else:
        dashboard(st.session_state["token"])


if __name__ == "__main__":
    main()