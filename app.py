import os
import json
import streamlit as st
import pandas as pd
import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# ✅ Zorg ervoor dat alle benodigde pakketten zijn geïnstalleerd
os.system("pip install -r requirements.txt")

# ✅ Streamlit UI Instellingen
st.set_page_config(page_title="AI Ondersteund Materiaalonderzoek", layout="wide")
st.title("🔬 AI Ondersteund Materiaalonderzoek")
st.write("Welkom bij je AI-gestuurde onderzoeksapp! 🚀")

# ✅ OpenAI API Sleutel invoeren
api_key = st.text_input("🔑 Voer je OpenAI API sleutel in:", type="password")

# ✅ AI Model Kiezen
model = st.selectbox("🤖 Kies een AI-model:", ["gpt-3.5-turbo", "gpt-4"])

# ✅ Onderzoeksvraag invoeren
onderzoeksvraag = st.text_area("📄 Voer je onderzoeksvraag in:")

# ✅ AI-gestuurd Literatuuronderzoek
if st.button("🔍 Zoek Literatuur"):
    if api_key and onderzoeksvraag:
        try:
            # ✅ Maak verbinding met OpenAI
            llm = ChatOpenAI(model=model, temperature=0.3, openai_api_key=api_key)

            # ✅ Maak de prompt voor AI
            prompt = PromptTemplate(
                input_variables=["onderzoeksvraag"],
                template="Geef een overzicht van de meest relevante literatuur over {onderzoeksvraag}."
            )

            # ✅ Vraag OpenAI om een antwoord
            antwoord = llm.invoke(prompt.format(onderzoeksvraag=onderzoeksvraag))

            # ✅ Debug: toon de ruwe output
            st.subheader("🛠 AI-Ruwe Output (Debug)")
            st.json(antwoord)  # Toont de volledige JSON-response voor debugging

            # ✅ Extract AI-content uit OpenAI JSON-output
            try:
                if isinstance(antwoord, str):
                    antwoord_dict = json.loads(antwoord)
                else:
                    antwoord_dict = antwoord  # Gebruik direct als het al een dictionary is

                # ✅ Controleer of het OpenAI-formaat klopt
                if isinstance(antwoord_dict, dict) and "choices" in antwoord_dict:
                    # ✅ Haal de daadwerkelijke AI-tekst eruit
                    ai_text = antwoord_dict["choices"][0]["message"]["content"]

                    st.subheader("📚 AI-Antwoord:")
                    st.write(ai_text)  # Toon alleen de AI-gegenereerde content
                else:
                    st.warning("⚠ Geen geldig AI-antwoord ontvangen. Controleer de API-output.")

            except json.JSONDecodeError:
                st.error("❌ Fout bij het verwerken van de AI-uitvoer. Probeer het opnieuw.")
            except Exception as e:
                st.error(f"❌ Onverwachte fout: {e}")

        except Exception as e:
            st.error(f"❌ Fout bij het aanroepen van OpenAI API: {e}")
    else:
        st.warning("⚠ Voer zowel een API-sleutel als een onderzoeksvraag in!")

# ✅ Meetdata uploaden en analyseren
st.subheader("📂 Upload meetdata (CSV-formaat)")
uploaded_file = st.file_uploader("📎 Kies een CSV-bestand", type=["csv"])

if uploaded_file:
    try:
        metingen = pd.read_csv(uploaded_file)
        st.write("📊 Geüploade Meetdata:")
        st.dataframe(metingen)

        # ✅ Vergelijking met literatuurwaarden
        literatuur_waarden = {"gemiddelde": 0.10, "tolerantie": 0.02}
        metingen["afwijking"] = metingen["efflorescentie"] - literatuur_waarden["gemiddelde"]
        metingen["acceptabel"] = metingen["afwijking"].abs() <= literatuur_waarden["tolerantie"]

        st.subheader("📊 Vergelijking met Literatuur:")
        st.dataframe(metingen)

    except Exception as e:
        st.error(f"❌ Fout bij het verwerken van de meetdata: {e}")

# ✅ Automatisch een rapport genereren
if uploaded_file and st.button("📄 Genereer Rapport"):
    try:
        rapport_prompt = PromptTemplate(
            input_variables=["metingen", "literatuur"],
            template="""
            Op basis van de uitgevoerde metingen en literatuurvergelijking zijn de volgende resultaten gevonden:

            - Gemeten efflorescentie: {metingen}
            - Vergelijking met literatuur: {literatuur}

            Op basis hiervan worden de volgende verbeteringen voorgesteld:
            """
        )

        llm = ChatOpenAI(model=model, temperature=0.3, openai_api_key=api_key)  # ✅ Zorg ervoor dat `llm` correct wordt aangemaakt

        rapport = llm.invoke(rapport_prompt.format(
            metingen=str(metingen),
            literatuur="Volgens studies is de gemiddelde efflorescentie 0.10 mg/cm²."
        ))

        # ✅ Debugging: Toon de ruwe output
        st.subheader("🛠 AI-Ruwe Output (Debug)")
        st.json(rapport)  # Toont de volledige JSON-response voor debugging

        # ✅ Extract AI-content uit OpenAI JSON-output
        try:
            if isinstance(rapport, str):
                rapport_dict = json.loads(rapport)
            else:
                rapport_dict = rapport

            if isinstance(rapport_dict, dict) and "choices" in rapport_dict:
                ai_text = rapport_dict["choices"][0]["message"]["content"]
                st.subheader("📄 Gegenereerd Rapport")
                st.write(ai_text)
            else:
                st.warning("⚠ Geen geldig AI-antwoord ontvangen. Controleer de API-output.")

        except json.JSONDecodeError:
            st.error("❌ Fout bij het verwerken van de AI-uitvoer. Probeer het opnieuw.")
        except Exception as e:
            st.error(f"❌ Onverwachte fout: {e}")

    except Exception as e:
        st.error(f"❌ Fout bij het genereren van het rapport: {e}")
