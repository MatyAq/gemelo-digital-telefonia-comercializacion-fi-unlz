import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Gemelo Digital de Consumidores | Comercialización FI-UNLZ", page_icon="📱", layout="wide")

EMPRESAS = ["Claro", "Personal", "Movistar"]
SEGMENTOS = ["Sensibles al precio", "Buscadores de GB", "Exigentes de cobertura", "Leales", "Insatisfechos"]

@st.cache_data
def generar_consumidores(n=100, seed=42):
    rng = np.random.default_rng(seed)
    empresas = rng.choice(EMPRESAS, size=n, p=[0.34, 0.40, 0.26])
    segmentos = rng.choice(SEGMENTOS, size=n, p=[0.27, 0.20, 0.19, 0.19, 0.15])
    filas = []
    for i, (empresa, segmento) in enumerate(zip(empresas, segmentos), start=1):
        precio = int(np.clip(rng.normal(22000, 5500), 9000, 42000))
        gb = int(rng.choice([5, 8, 10, 15, 20, 25, 30, 50], p=[.06,.08,.16,.17,.19,.12,.14,.08]))
        satisfaccion = int(np.clip(round(rng.normal(7, 1.5)), 1, 10))
        imp_precio = int(np.clip(round(rng.normal(7, 1.7)), 1, 10))
        imp_gb = int(np.clip(round(rng.normal(6.5, 1.8)), 1, 10))
        imp_senal = int(np.clip(round(rng.normal(8, 1.4)), 1, 10))
        imp_atencion = int(np.clip(round(rng.normal(6, 1.8)), 1, 10))
        antiguedad = int(np.clip(round(rng.normal(3.2, 2.1)), 0, 10))
        disposicion = int(np.clip(round(rng.normal(5, 2.2)), 0, 10))

        if segmento == "Sensibles al precio":
            imp_precio = int(np.clip(imp_precio + 2, 1, 10))
            disposicion = int(np.clip(disposicion + 1, 0, 10))
        elif segmento == "Buscadores de GB":
            imp_gb = int(np.clip(imp_gb + 3, 1, 10))
        elif segmento == "Exigentes de cobertura":
            imp_senal = int(np.clip(imp_senal + 2, 1, 10))
        elif segmento == "Leales":
            antiguedad = int(np.clip(antiguedad + 3, 0, 12))
            satisfaccion = int(np.clip(satisfaccion + 1, 1, 10))
            disposicion = int(np.clip(disposicion - 2, 0, 10))
        elif segmento == "Insatisfechos":
            satisfaccion = int(np.clip(satisfaccion - 3, 1, 10))
            disposicion = int(np.clip(disposicion + 3, 0, 10))

        filas.append({
            "ID": f"C{i:03d}",
            "Empresa_actual": empresa,
            "Segmento": segmento,
            "Precio_mensual": precio,
            "GB_plan": gb,
            "Satisfaccion": satisfaccion,
            "Importancia_precio": imp_precio,
            "Importancia_GB": imp_gb,
            "Importancia_senal": imp_senal,
            "Importancia_atencion": imp_atencion,
            "Antiguedad_anios": antiguedad,
            "Disposicion_cambio": disposicion,
        })
    return pd.DataFrame(filas)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def simular_oferta(df, ofertante, descuento_pct, gb_extra, mejora_senal, promo_meses):
    sim = df.copy()
    elegible = sim["Empresa_actual"] != ofertante
    descuento = descuento_pct / 100.0
    sens_precio = sim["Importancia_precio"] / 10
    sens_gb = sim["Importancia_GB"] / 10
    sens_senal = sim["Importancia_senal"] / 10
    insatisfaccion = (10 - sim["Satisfaccion"]) / 9
    predisposicion = sim["Disposicion_cambio"] / 10
    lealtad = np.clip((sim["Antiguedad_anios"] / 10) * (sim["Satisfaccion"] / 10), 0, 1)

    efecto_precio = descuento * 3.0 * sens_precio
    efecto_gb = min(gb_extra / 30.0, 1.5) * 1.35 * sens_gb
    efecto_senal = (mejora_senal / 3.0) * 1.45 * sens_senal
    efecto_promo = min(promo_meses / 12.0, 1.0) * 0.75

    score = (-2.35 + 1.35 * predisposicion + 1.30 * insatisfaccion - 1.10 * lealtad + efecto_precio + efecto_gb + efecto_senal + efecto_promo)
    prob = sigmoid(score)
    prob = np.where(elegible, prob, 0.0)
    sim["Probabilidad_cambio"] = prob
    sim["Cambio_predicho"] = sim["Probabilidad_cambio"] >= 0.50
    sim["Empresa_simulada"] = np.where(sim["Cambio_predicho"], ofertante, sim["Empresa_actual"])
    return sim

df = generar_consumidores()

st.title("📱 Gemelo Digital simplificado de consumidores de telefonía")
st.caption("Comercialización · Facultad de Ingeniería · UNLZ")
st.info("Esta versión usa 100 consumidores sintéticos para fines docentes. Funciona como un prototipo de gemelo digital de mercado: representa consumidores, simula ofertas y permite comparar escenarios. Cuando se reemplacen estos datos por encuestas reales y se actualicen con nuevas mediciones, el vínculo con el mercado real será mucho más fuerte.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Mercado actual", "🧪 ¿Qué pasaría si...?", "👥 Perfiles", "🔁 De modelo a gemelo"])

with tab1:
    st.subheader("Mercado sintético de partida")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Consumidores", len(df))
    c2.metric("Gasto promedio", f"${df['Precio_mensual'].mean():,.0f}".replace(",", "."))
    c3.metric("Satisfacción promedio", f"{df['Satisfaccion'].mean():.1f}/10")
    c4.metric("Disposición a cambiar", f"{df['Disposicion_cambio'].mean():.1f}/10")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Participación actual")
        share = df["Empresa_actual"].value_counts().reindex(EMPRESAS).fillna(0).rename("Consumidores")
        st.bar_chart(share)
    with col_b:
        st.markdown("#### Segmentos")
        seg = df["Segmento"].value_counts().rename("Consumidores")
        st.bar_chart(seg)

    st.markdown("#### Base de consumidores")
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🧪 ¿Qué pasaría si...?")
    st.write("Diseñá una oferta comercial. El sistema evalúa a cada consumidor sintético y estima su probabilidad de cambiar hacia la empresa ofertante.")
    c1, c2 = st.columns([1, 2])
    with c1:
        ofertante = st.selectbox("Empresa que lanza la oferta", EMPRESAS)
        descuento = st.slider("Descuento sobre el precio actual", 0, 35, 15, 5, format="%d%%")
        gb_extra = st.slider("GB adicionales", 0, 50, 10, 5)
        mejora_senal = st.slider("Mejora percibida de cobertura/señal", 0, 3, 1, help="0 = sin cambio · 1 = leve · 2 = importante · 3 = muy importante")
        promo_meses = st.slider("Duración de la promoción (meses)", 0, 12, 6, 1)
        st.markdown("**Oferta simulada**")
        st.write(f"**{ofertante}** ofrece **{descuento}% de descuento**, **{gb_extra} GB extra**, mejora de señal **{mejora_senal}/3** durante **{promo_meses} meses**.")

    sim = simular_oferta(df, ofertante, descuento, gb_extra, mejora_senal, promo_meses)
    elegibles = sim[sim["Empresa_actual"] != ofertante]
    cambios = sim[sim["Cambio_predicho"]]
    esperados = elegibles["Probabilidad_cambio"].sum()

    with c2:
        m1, m2, m3 = st.columns(3)
        m1.metric("Clientes elegibles", len(elegibles))
        m2.metric("Cambios predichos", len(cambios))
        m3.metric("Cambios esperados", f"{esperados:.1f}")
        actual = df["Empresa_actual"].value_counts().reindex(EMPRESAS).fillna(0)
        despues = sim["Empresa_simulada"].value_counts().reindex(EMPRESAS).fillna(0)
        comp = pd.DataFrame({"Actual": actual, "Simulado": despues})
        st.markdown("#### Participación: antes vs. después")
        st.bar_chart(comp)

    st.markdown("#### ¿De qué empresas vendrían los nuevos clientes?")
    origen = cambios["Empresa_actual"].value_counts().reindex([e for e in EMPRESAS if e != ofertante]).fillna(0).rename("Cambios")
    st.bar_chart(origen)

    st.markdown("#### ¿Qué perfiles responden más?")
    if len(cambios) > 0:
        st.bar_chart(cambios["Segmento"].value_counts().rename("Cambios"))
    else:
        st.warning("Con esta oferta, ningún consumidor supera el umbral de cambio del 50%.")

    st.markdown("#### Consumidores con mayor probabilidad de cambiar")
    top = sim[sim["Empresa_actual"] != ofertante].sort_values("Probabilidad_cambio", ascending=False).head(15).copy()
    top["Probabilidad_cambio"] = (top["Probabilidad_cambio"] * 100).round(1)
    st.dataframe(top[["ID", "Empresa_actual", "Segmento", "Precio_mensual", "GB_plan", "Satisfaccion", "Disposicion_cambio", "Probabilidad_cambio"]], use_container_width=True, hide_index=True)
    st.warning("Importante: estas probabilidades provienen de reglas sintéticas creadas para enseñar la lógica de simulación. No deben interpretarse como predicciones reales del mercado.")

with tab3:
    st.subheader("👥 El mercado no es un consumidor promedio")
    st.write("El prototipo representa consumidores individuales. Por eso una misma oferta puede producir respuestas distintas según el perfil.")
    segmento_elegido = st.selectbox("Elegí un segmento", SEGMENTOS)
    muestra = df[df["Segmento"] == segmento_elegido]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Personas", len(muestra))
    c2.metric("Imp. precio", f"{muestra['Importancia_precio'].mean():.1f}/10")
    c3.metric("Imp. GB", f"{muestra['Importancia_GB'].mean():.1f}/10")
    c4.metric("Imp. señal", f"{muestra['Importancia_senal'].mean():.1f}/10")
    perfil = pd.DataFrame({
        "Variable": ["Precio", "GB", "Señal", "Atención", "Satisfacción", "Disposición cambio"],
        "Promedio": [muestra["Importancia_precio"].mean(), muestra["Importancia_GB"].mean(), muestra["Importancia_senal"].mean(), muestra["Importancia_atencion"].mean(), muestra["Satisfaccion"].mean(), muestra["Disposicion_cambio"].mean()]
    }).set_index("Variable")
    st.bar_chart(perfil)
    st.dataframe(muestra, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("🔁 ¿Cuándo esto se acerca más a un verdadero gemelo digital?")
    st.markdown("""
### Nivel 1 — Datos
Encuestamos consumidores reales.

### Nivel 2 — Modelo digital
Representamos digitalmente sus características y reglas de comportamiento.

### Nivel 3 — Simulación
Probamos escenarios: precio, GB, señal, promociones.

### Nivel 4 — Validación
Comparamos lo que predijo el modelo con lo que efectivamente ocurrió.

### Nivel 5 — Actualización
Volvemos a medir el mercado y recalibramos el modelo.

**Consumidores reales → datos → modelo → simulación → decisión → nueva medición → actualización**
    """)
    st.success("Para la clase: esta versión es un prototipo con datos sintéticos. El siguiente paso es reemplazar la base por la encuesta real de los alumnos.")
    st.markdown("#### Futuro: cargar la encuesta real")
    archivo = st.file_uploader("Podés cargar un CSV para mostrar cómo sería el reemplazo de la base sintética.", type=["csv"])
    if archivo is not None:
        try:
            real = pd.read_csv(archivo)
            st.write(f"Archivo recibido: **{len(real)} filas**")
            st.dataframe(real.head(20), use_container_width=True)
            st.info("Cuando tengamos la encuesta definitiva, puedo adaptar la app para que este archivo reemplace realmente a la base sintética y alimente el simulador.")
        except Exception as e:
            st.error(f"No pude leer el CSV: {e}")

st.divider()
st.caption("Prototipo docente · Comercialización · FI-UNLZ · Los datos y parámetros son sintéticos y no representan participación ni comportamiento real de las compañías.")
