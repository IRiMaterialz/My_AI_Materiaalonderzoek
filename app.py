import os
os.system("pip install -r requirements.txt")

import streamlit as st

st.title("AI Ondersteund Materiaalonderzoek")
st.write("Welkom bij je AI-gestuurde onderzoeksapp!")
import streamlit as st

import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

st.title("AI Ondersteund Materiaalonderzoek")
st.write("Welkom bij je AI-gestuurde onderzoeksapp!")

# 🔹 OpenAI API Sleutel invoeren
api_key = st.text_input("Voer je OpenAI API sleutel in:", type="password")

# 🔹 AI Model Kiezen
model = st.selectbox("Kies een model:", ["gpt-3.5-turbo", "gpt-4"])

# 🔹 Onderzoeksvraag invoeren
onderzoeksvraag = st.text_area("Voer je onderzoeksvraag in:")

if st.button("Zoek Literatuur"):
    if api_key and onderzoeksvraag:
        llm = ChatOpenAI(model=model, temperature=0.3, openai_api_key=api_key)

        prompt = PromptTemplate(
            input_variables=["onderzoeksvraag"],
            template="Geef een overzicht van de meest relevante literatuur over {onderzoeksvraag}."
        )
        
        antwoord = llm.invoke(prompt.format(onderzoeksvraag=onderzoeksvraag))
        st.subheader("AI-Antwoord:")
import json
import streamlit as st

# Controleer of de AI-reactie een geldig JSON-object is
try:
    antwoord_dict = json.loads(antwoord.json())  # Zet om naar een Python dictionary
    
    # Controleer of 'content' in het antwoord zit en toon het
    if "content" in antwoord_dict:
        st.subheader("AI-Antwoord:")
        st.write(antwoord_dict["content"])  # Alleen de relevante tekst weergeven
    else:
        st.warning("Geen geldig AI-antwoord ontvangen.")

except json.JSONDecodeError:
    st.error("Fout bij verwerken van AI-reactie. Probeer het opnieuw.")

    else:
        st.warning("Voer zowel een API sleutel als een onderzoeksvraag in!")

import pandas as pd

st.subheader("Upload meetdata (CSV-formaat)")
uploaded_file = st.file_uploader("Kies een CSV-bestand", type=["csv"])

if uploaded_file:
    metingen = pd.read_csv(uploaded_file)
    st.write("Geüploade Meetdata:")
    st.dataframe(metingen)

    # 🔹 Vergelijking met literatuurwaarden
    literatuur_waarden = {"gemiddelde": 0.10, "tolerantie": 0.02}
    metingen["afwijking"] = metingen["efflorescentie"] - literatuur_waarden["gemiddelde"]
    metingen["acceptabel"] = metingen["afwijking"].abs() <= literatuur_waarden["tolerantie"]
    
    st.subheader("Vergelijking met Literatuur:")
    st.dataframe(metingen)

if uploaded_file and st.button("Genereer Rapport"):
    rapport_prompt = PromptTemplate(
        input_variables=["metingen", "literatuur"],
        template="""
        Op basis van de uitgevoerde metingen en literatuurvergelijking zijn de volgende resultaten gevonden:

        - Gemeten efflorescentie: {metingen}
        - Vergelijking met literatuur: {literatuur}

        Op basis hiervan worden de volgende verbeteringen voorgesteld:
        """
    )

    rapport = llm.invoke(rapport_prompt.format(
        metingen=str(metingen),
        literatuur="Volgens studies is de gemiddelde efflorescentie 0.10 mg/cm²."
    ))

    st.subheader("Gegenereerd Rapport")
    st.write(rapport)
