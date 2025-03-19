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

# ✅ Debug Mode (schakel aan/uit voor debugging)
DEBUG_MODE = False  # Zet op True om debugging aan te zetten

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

            # ✅ Maak de prompt voor AI (10 studies met bronvermelding)
            prompt = PromptTemplate(
                input_variables=["onderzoeksvraag"],
                template="""
                Geef een overzicht van de 10 meest relevante wetenschappelijke studies over {onderzoeksvraag}, 
                inclusief een korte samenvatting en de bronvermelding (auteur, titel, publicatiejaar, en DOI of link indien beschikbaar).
                """
            )

            # ✅ Vraag OpenAI om een antwoord
            antwoord = llm.invoke(prompt.format(onderzoeksvraag=onderzoeksvraag))

            # ✅ Haal alleen de AI-content eruit
            if hasattr(antwoord, "content"):
                st.subheader("📚 AI-Antwoord: 10 Wetenschappelijke Studies met Bronvermelding")
                st.write(antwoord.content)  # Toon alleen de relevante AI-output
            else:
                st.warning("⚠ Geen geldig AI-antwoord ontvangen. Controleer de API-output.")

        except Exception as e:
            st.error(f"❌ Fout bij het verwerken van de AI-uitvoer: {e}")
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

        # ✅ (Optioneel) Debug: Toon de kolomnamen om fouten te voorkomen
        if DEBUG_MODE:
            st.subheader("🛠 CSV Kolomnamen (Debug)")
            st.write(metingen.columns.tolist())  # Toon alle kolomnamen
        
        # ✅ Controleer of de kolom 'efflorescentie' bestaat
        if "efflorescentie" not in metingen.columns:
            st.error("❌ Fout: De kolom 'efflorescentie' ontbreekt in het CSV-bestand.")
            st.warning("⚠ Controleer de CSV en hernoem de kolom naar 'efflorescentie' als dat nodig is.")
        else:
            # ✅ Vergelijking met literatuurwaarden uitvoeren
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

        # ✅ Haal alleen de AI-content eruit
        if hasattr(rapport, "content"):
            st.subheader("📄 Gegenereerd Rapport")
            st.write(rapport.content)
        else:
            st.warning("⚠ Geen geldig AI-antwoord ontvangen. Controleer de API-output.")

    except Exception as e:
        st.error(f"❌ Fout bij het genereren van het rapport: {e}")
