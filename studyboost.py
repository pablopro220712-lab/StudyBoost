import random
import re

import streamlit as st

st.set_page_config(page_title="StudyBoost", page_icon="🧠", layout="centered")

defaults = {
    "tarjetas": [],
    "i": 0,
    "mostrar": False,
    "ok": 0,
    "fail": 0,
    "test": None,
    "corregido": False,
}
for clave, valor in defaults.items():
    st.session_state.setdefault(clave, valor)


def extraer_tarjetas(texto):
    tarjetas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if ":" in linea:
            p, r = linea.split(":", 1)
        else:
            m = re.match(r"(.+?)\s+(es|son|fue|fueron)\s+(.+)", linea, re.I)
            if not m:
                continue
            p, r = m.group(1), f"{m.group(2)} {m.group(3)}"
        if p.strip() and r.strip():
            tarjetas.append({"pregunta": p.strip(), "respuesta": r.strip()})
    return tarjetas


def crear_test(tarjetas, n=5):
    test = []
    for t in random.sample(tarjetas, min(n, len(tarjetas))):
        otras = [x["respuesta"] for x in tarjetas if x is not t]
        opciones = random.sample(otras, min(3, len(otras))) + [t["respuesta"]]
        random.shuffle(opciones)
        test.append({"pregunta": t["pregunta"], "correcta": t["respuesta"], "opciones": opciones})
    return test


def responder(sabia):
    st.session_state.ok += 1 if sabia else 0
    st.session_state.fail += 0 if sabia else 1
    st.session_state.i = (st.session_state.i + 1) % len(st.session_state.tarjetas)
    st.session_state.mostrar = False


st.title("🧠 StudyBoost")
st.caption("Pega tus apuntes y estudia con flashcards y tests al instante 🚀")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Apuntes", "🃏 Flashcards", "✅ Test", "📈 Progreso"])

with tab1:
    texto = st.text_area("Pega aquí tus apuntes (una idea por línea)", height=220)
    if st.button("✨ Generar tarjetas", type="primary"):
        st.session_state.tarjetas = extraer_tarjetas(texto)
        st.session_state.i, st.session_state.test = 0, None
        n = len(st.session_state.tarjetas)
        if n:
            st.success(f"¡{n} tarjetas creadas! 🎉")
        else:
            st.warning("No encontré ideas. Usa el formato 'Término: definición' 🙂")

tarjetas = st.session_state.tarjetas

with tab2:
    if not tarjetas:
        st.info("Primero genera tarjetas en la pestaña Apuntes 📝")
    else:
        t = tarjetas[st.session_state.i]
        st.progress((st.session_state.i + 1) / len(tarjetas))
        st.subheader(f"❓ {t['pregunta']}")
        if st.session_state.mostrar:
            st.success(f"💡 {t['respuesta']}")
            c1, c2 = st.columns(2)
            c1.button("✅ La sabía", on_click=responder, args=(True,), use_container_width=True)
            c2.button("❌ No la sabía", on_click=responder, args=(False,), use_container_width=True)
        else:
            if st.button("👀 Mostrar respuesta", use_container_width=True):
                st.session_state.mostrar = True
                st.rerun()

with tab3:
    if len(tarjetas) < 4:
        st.info("Necesitas al menos 4 tarjetas para hacer un test 🎯")
    else:
        if st.button("🎲 Nuevo test"):
            st.session_state.test = crear_test(tarjetas)
            st.session_state.corregido = False
        test = st.session_state.test
        if test:
            respuestas = []
            for n, q in enumerate(test, 1):
                respuestas.append(st.radio(f"{n}. {q['pregunta']}", q["opciones"], index=None, key=f"q{n}"))
            if st.button("📤 Corregir"):
                st.session_state.corregido = True
            if st.session_state.corregido:
                aciertos = sum(r == q["correcta"] for r, q in zip(respuestas, test))
                st.metric("Nota", f"{aciertos}/{len(test)}")
                for q, r in zip(test, respuestas):
                    if r != q["correcta"]:
                        st.error(f"❌ {q['pregunta']} → {q['correcta']}")
                if aciertos == len(test):
                    st.balloons()

with tab4:
    total = st.session_state.ok + st.session_state.fail
    a, b, c = st.columns(3)
    a.metric("✅ Aciertos", st.session_state.ok)
    b.metric("❌ Fallos", st.session_state.fail)
    c.metric("🎯 Precisión", f"{round(100 * st.session_state.ok / total) if total else 0}%")
