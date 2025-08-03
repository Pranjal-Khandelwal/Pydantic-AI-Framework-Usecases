# app.py

import streamlit as st
from datetime import datetime
from ollama_utils import run_ollama, search_duckduckgo
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")

st.markdown("""
    <style>
        .title { text-align: center; font-size: 36px; font-weight: bold; color: #ff5733; }
        .subtitle { text-align: center; font-size: 20px; color: #555; }
        .stSlider > div { background-color: #f9f9f9; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

# Inputs
st.markdown("### 🌍 Where are you headed?")
source = st.text_input("🛫 Departure City (IATA Code):", "BOM")
destination = st.text_input("🛬 Destination (IATA Code):", "DEL")

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox("🎭 Select Your Travel Theme:", ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"])

st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; padding: 15px; background-color: #ffecd1; border-radius: 10px; margin-top: 20px;">
        <h3>🌟 Your {travel_theme} to {destination} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
""", unsafe_allow_html=True)

activity_preferences = st.text_area("🌍 What activities do you enjoy?", "Relaxing on the beach, exploring historical sites")
departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

# Sidebar
st.sidebar.title("🌎 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")
budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

def generate_pdf(destination, flights_info, hotel_info, itinerary):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>🌍 Travel Plan to {destination}</b>", styles['Title']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>✈️ Flights Summary</b>", styles['Heading2']))
    elements.append(Paragraph(flights_info.replace("\n", "<br/>"), styles['BodyText']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>🏨 Hotels & Restaurants</b>", styles['Heading2']))
    elements.append(Paragraph(hotel_info.replace("\n", "<br/>"), styles['BodyText']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>🗺️ Personalized Itinerary</b>", styles['Heading2']))
    elements.append(Paragraph(itinerary.replace("\n", "<br/>"), styles['BodyText']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("🚀 Generate Travel Plan"):
    with st.spinner("✈️ Searching for flight information..."):
        flights_info = search_duckduckgo(f"Flights from {source} to {destination} on {departure_date}")

    with st.spinner("🔍 Researching attractions & activities..."):
        search_snippets = search_duckduckgo(f"Top things to do in {destination} for a {travel_theme.lower()} trip")
        research_prompt = (
            f"You are a travel assistant. Summarize and recommend activities based on this information:\n\n{search_snippets}\n\n"
            f"User preferences: enjoys {activity_preferences}, budget: {budget}, hotel: {hotel_rating}, trip duration: {num_days} days."
        )
        research_results = run_ollama(research_prompt)

    with st.spinner("🏨 Searching for hotels & restaurants..."):
        search_snippets_hotels = search_duckduckgo(f"Best hotels and restaurants in {destination}")
        hotel_prompt = (
            f"Based on the following results, suggest good hotels and restaurants in {destination} for a {travel_theme.lower()} trip.\n\n"
            f"{search_snippets_hotels}\n\nUser prefers: {hotel_rating} hotels, {budget} budget."
        )
        hotel_restaurant_results = run_ollama(hotel_prompt)

    with st.spinner("🗺️ Creating your personalized itinerary..."):
        planning_prompt = (
            f"Create a detailed {num_days}-day itinerary for a {travel_theme.lower()} trip to {destination}. "
            f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
            f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. Research: {research_results}. "
            f"Flight Info: {flights_info}. Hotels & Restaurants: {hotel_restaurant_results}."
        )
        itinerary = run_ollama(planning_prompt)

    # Output
    st.subheader("✈️ Flights Summary")
    st.write(flights_info)

    st.subheader("🏨 Hotels & Restaurants")
    st.write(hotel_restaurant_results)

    st.subheader("🗺️ Your Personalized Itinerary")
    st.write(itinerary)

    st.success("✅ Travel plan generated successfully!")

    # Markdown Download Option
    markdown_content = f"""
# 🌍 Travel Plan to {destination}

## ✈️ Flights Summary
{flights_info}

## 🏨 Hotels & Restaurants
{hotel_restaurant_results}

## 🗺️ Personalized Itinerary
{itinerary}
"""
    st.download_button(
        label="📥 Download Travel Plan (.md)",
        data=markdown_content,
        file_name=f"{destination}_travel_plan.md",
        mime="text/markdown"
    )

    # PDF Download using ReportLab
    pdf_buffer = generate_pdf(destination, flights_info, hotel_restaurant_results, itinerary)

    st.download_button(
        label="📄 Download Travel Plan (.pdf)",
        data=pdf_buffer,
        file_name=f"{destination}_travel_plan.pdf",
        mime="application/pdf"
    )