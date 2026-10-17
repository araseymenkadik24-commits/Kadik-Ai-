import os
import streamlit as st
from google import genai
from google.genai import types
from ddgs import DDGS

try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

MODEL = "gemini-3.5-flash"
SISTEM = (
    "Senin adın Kadık AI. Kullanıcıya Türkçe ve samimi şekilde cevap ver. "
    "Sana internet arama sonuçları verilirse cevabı onlara dayandır. "
    "Sonuçlarda cevap yoksa bunu dürüstçe söyle, tahmin yürütme."
)

st.set_page_config(page_title="Kadık AI", page_icon="🤖")
st.title("Kadık AI")
st.caption("Internette arama yapabilen Türk yapay zekâsı. Girdiğin sorular Google'a gönderilir, kişisel bilgi yazma.")

client = genai.Client()


def ara(soru):
    sonuclar = DDGS().text(soru, region="tr-tr", max_results=5)
    return "".join(
        f"Başlık: {s['title']}\nÖzet: {s['body']}\nLink: {s['href']}\n\n"
        for s in sonuclar
    )


if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = []

for m in st.session_state.mesajlar:
    with st.chat_message(m["rol"]):
        st.write(m["metin"])

soru = st.chat_input("Sormak istediğin şeyi yaz")

if soru:
    st.session_state.mesajlar.append({"rol": "user", "metin": soru})
    with st.chat_message("user"):
        st.write(soru)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            try:
                istek = f"Soru: {soru}\n\nİnternet arama sonuçları:\n{ara(soru)}"
            except Exception:
                istek = soru

            gecmis = [
                types.Content(
                    role="user" if m["rol"] == "user" else "model",
                    parts=[types.Part(text=m["metin"])],
                )
                for m in st.session_state.mesajlar[:-1][-6:]
            ]
            gecmis.append(types.Content(role="user", parts=[types.Part(text=istek)]))

            try:
                cevap = client.models.generate_content(
                    model=MODEL,
                    contents=gecmis,
                    config=types.GenerateContentConfig(system_instruction=SISTEM),
                ).text
            except Exception as e:
                cevap = "Şu an cevap veremiyorum, biraz sonra tekrar dene. (" + str(e)[:120] + ")"
        st.write(cevap)

    st.session_state.mesajlar.append({"rol": "assistant", "metin": cevap})
    