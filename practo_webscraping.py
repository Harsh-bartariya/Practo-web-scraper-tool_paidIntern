import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

# Set up the Streamlit page configuration
st.set_page_config(page_title="Practo Doctor Scraper🩺", page_icon="🩺", layout="wide")

# Page and Input Section
st.title("Practo Doctor Finder")

# Dynamic Inputs: City and Specialization
city_name = st.text_input("Enter the city name:")
specializations = [
    "Cardiologist", "Dentist", "Dermatologist", "ENT Specialist",
    "General Physician", "Gynecologist", "Neurologist", "Orthopedic",
    "Pediatrician", "Psychiatrist", "Radiologist", "Urologist"
]
doctor_speciality = st.selectbox("Select a specialization:", specializations)

# Function to fetch page content using the Requests library
def fetch_page_content(city, speciality, page=1):
    base_url = "https://www.practo.com/search/doctors"
    specialization_query = urllib.parse.quote(f'[{{"word":"{speciality}","autocompleted":true,"category":"subspeciality"}}]')
    full_url = f"{base_url}?results_type=doctor&q={specialization_query}&city={city}&page={page}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(full_url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        return None

def parse_doctor_data(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Extract doctor profiles
    doctors = []
    doctor_elements = soup.find_all("div", class_="info-section")
    
    for element in doctor_elements:
        # Find the anchor tag that contains the hyperlink
        link_tag = element.find("a")
        relative_profile_link = link_tag["href"] if link_tag else None
        base_url = "https://www.practo.com"
        profile_link = urllib.parse.urljoin(base_url, relative_profile_link) if relative_profile_link else "Link not found"
        
        # Now find the doctor's name within the anchor tag
        name = link_tag.find("h2", {"data-qa-id": "doctor_name"}).text.strip() if link_tag and link_tag.find("h2", {"data-qa-id": "doctor_name"}) else "Name not found"
        
        specialization = element.find("div", class_="u-d-flex").text.strip() if element.find("div", class_="u-d-flex") else "Specialization not found"
        experience = element.find("div", {"data-qa-id": "doctor_experience"}).text.strip() if element.find("div", {"data-qa-id": "doctor_experience"}) else "Experience not found"
        clinic_name = element.find("span", {"data-qa-id": "doctor_clinic_name"}).text.strip() if element.find("span", {"data-qa-id": "doctor_clinic_name"}) else "Clinic name not found"
        practice_locality = element.find("span", {"data-qa-id": "practice_locality"}).text.strip() if element.find("span", {"data-qa-id": "practice_locality"}) else "Practice locality not found"
        consultation_fees = element.find("span", {"data-qa-id": "consultation_fee"}).text.strip() if element.find("span", {"data-qa-id": "consultation_fee"}) else "Consultation fee not found"

        doctors.append({
            "name": name,
            "profile_link": profile_link,  # Adding the full link to the dictionary
            "specialization": specialization,
            "experience": experience,
            "clinic_name": clinic_name,
            "practice_locality": practice_locality,
            "consultation_fees": consultation_fees
        })
    
    return doctors

# Function to structure the scraped data using Pandas
def structure_data(doctors):
    # Structuring data with Pandas for easier manipulation and display
    df = pd.DataFrame(doctors)
    return df

# Main logic for handling user inputs and displaying the results
if st.button("Find Doctors"):
    if city_name and doctor_speciality:
        doctors_data = []
        page = 1
        
        while True:
            page_content = fetch_page_content(city_name, doctor_speciality, page)
            if not page_content:
                break
            
            doctors = parse_doctor_data(page_content)
            if not doctors:
                break
            
            doctors_data.extend(doctors)
            page += 1
        
        if doctors_data:
            df = structure_data(doctors_data)
            st.write(f"Total number of doctor profiles found: {len(df)}")
            st.table(df)
        else:
            st.warning("No doctors found.")
    else:
        st.error("Please enter both city and specialization.")
