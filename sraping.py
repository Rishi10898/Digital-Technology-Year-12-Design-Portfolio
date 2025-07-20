import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Playwright, expect
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load environment variables from .env file
load_dotenv()

# --- MongoDB Configuration ---
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in .env file. Please set it.")

def get_mongo_collection():
    """Establishes MongoDB connection and returns the collection."""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        print("Connected to MongoDB Atlas successfully!")
        return collection
    except PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        # Exit or handle gracefully if DB connection fails
        raise

# --- Scraper Logic ---

def scrape_university_programme(page, programme_url):
    """
    Scrapes a single university programme page and extracts detailed data.
    You will need to heavily customize this function for each university.
    """
    print(f"Navigating to: {programme_url}")
    try:
        page.goto(programme_url, wait_until="domcontentloaded", timeout=60000)
        # Wait for dynamic content to load (adjust selectors as needed)
        page.wait_for_selector('h1.programme-title', timeout=30000)
        # Add more specific waits if content loads lazily
        # page.wait_for_selector('.entry-requirements-section', timeout=20000)

        data = {}

        # --- Extract Programme Name, Code, Level, Field ---
        try:
            data["programme"] = page.locator('h1.programme-title').text_content().strip()
        except Exception:
            print("Could not find programme title.")
            data["programme"] = "N/A" # Set default or skip if critical
            # Consider raising an error here if title is essential to proceed

        # Assuming you can extract these from surrounding text or specific elements
        # This will require custom logic for each site. Example placeholders:
        try:
            data["field"] = page.locator('span.programme-field').text_content().strip()
        except Exception:
            data["field"] = "N/A"
        try:
            data["Level"] = int(page.locator('span.programme-level').text_content().replace('Level', '').strip())
        except Exception:
            data["Level"] = None
        
        # This might be tricky, often on the same page or in URL
        data["programme_code"] = programme_url.split('/')[-1] # Simple guess, customize!

        # --- Extract Location, Duration, Points ---
        try:
            data["location"] = page.locator('.programme-location-info').text_content().strip()
        except Exception:
            data["location"] = "N/A"
        try:
            data["fulltime_duration_years"] = int(page.locator('.programme-duration').text_content().split(' ')[0])
        except Exception:
            data["fulltime_duration_years"] = None
        try:
            data["points"] = int(page.locator('.programme-points').text_content().replace('points', '').strip())
        except Exception:
            data["points"] = None

        # --- Extract Fees (handle year-specific data) ---
        # This is often complex and requires finding the specific year's fee.
        # It's better to store fees as a list of objects if multiple years are present.
        fees_2025_element = page.locator('.fees-2025').text_content() # Example selector
        if fees_2025_element:
            data["domestic_fee_NZD_2025_per_year_120_points"] = fees_2025_element.strip()
        else:
            data["domestic_fee_NZD_2025_per_year_120_points"] = "N/A"
        # For multiple years, you'd iterate through elements that contain fees by year.

        # --- Extract Links ---
        data["linkText"] = data["programme"] # Use programme name as link text
        data["link"] = programme_url
        
        # Example for specific guides, assuming they have unique selectors or patterns
        try:
            data["Degree_Builder"] = page.locator('a.degree-builder-link').get_attribute('href')
        except Exception:
            data["Degree_Builder"] = None
        
        try:
            data["Undergraduate_Programme_Guide_2025_link"] = page.locator('a.guide-2025-link').get_attribute('href')
        except Exception:
            data["Undergraduate_Programme_Guide_2025_link"] = None
        
        try:
            data["Undergraduate_Programme_Guide_2026_link"] = page.locator('a.guide-2026-link').get_attribute('href')
        except Exception:
            data["Undergraduate_Programme_Guide_2026_link"] = None


        # --- Extract "What you will study" (nested object) ---
        what_you_will_study = {}
        # This will vary greatly. You might look for h3/h4 tags followed by p/ul tags
        # Example: Find a section by its heading and extract content
        study_sections = page.query_selector_all('.study-section h3')
        for section in study_sections:
            section_title = section.text_content().strip()
            # Find sibling elements that contain the description/list
            description_elements = section.locator('+ p, + ul, + div').all() # Example siblings
            if description_elements:
                description_text = "\n".join([el.text_content().strip() for el in description_elements])
                what_you_will_study[section_title] = description_text
        data["What_you_will_study"] = what_you_will_study


        # --- Extract "Skills you will develop" ---
        try:
            data["Skills_you_will_develop"] = page.locator('.skills-section a').get_attribute('href') # Or text
        except Exception:
            data["Skills_you_will_develop"] = "N/A"


        # --- Extract Entry Requirements (nested object) ---
        entry_requirements = {}
        # This is usually structured with headings like NCEA, CIE, IB
        # You'll need to find these sections and extract their content.
        # Example for NCEA:
        try:
            ncea_text = page.locator('.entry-requirements-ncea').text_content().strip()
            entry_requirements["NCEA"] = ncea_text
        except Exception:
            pass # NCEA might not exist

        # Example for CIE (more nested):
        try:
            cie_section = page.locator('.entry-requirements-cie')
            if cie_section:
                entry_requirements["CIE"] = {
                    "Total": cie_section.locator('.cie-total').text_content().strip() if cie_section.locator('.cie-total') else None,
                    "UE literacy": cie_section.locator('.cie-literacy').text_content().strip() if cie_section.locator('.cie-literacy') else None,
                    "Numeracy": cie_section.locator('.cie-numeracy').text_content().strip() if cie_section.locator('.cie-numeracy') else None,
                }
        except Exception:
            pass

        # Similar logic for IB

        # Example for Useful_New_Zealand_School_Subjects (list)
        try:
            subjects_list = page.locator('.useful-subjects li').all_text_contents()
            entry_requirements["Useful_New_Zealand_School_Subjects"] = [s.strip() for s in subjects_list if s.strip()]
        except Exception:
            pass

        data["Entry Requirements"] = entry_requirements

        # --- Extract Majors and Minors (lists) ---
        try:
            majors_list = page.locator('.majors-list li').all_text_contents()
            data["Majors"] = [m.strip() for m in majors_list if m.strip()]
        except Exception:
            data["Majors"] = []
        
        try:
            minors_list = page.locator('.minors-list li').all_text_contents()
            data["Minors"] = [m.strip() for m in minors_list if m.strip()]
        except Exception:
            data["Minors"] = []


        # Add a timestamp for when this data was last scraped
        data["last_scraped_date"] = datetime.now()

        print(f"Successfully scraped: {data.get('programme', 'Unknown Programme')}")
        return data

    except Exception as e:
        print(f"Error scraping {programme_url}: {e}")
        return None

def main_scraper():
    collection = get_mongo_collection()

    # Define the list of URLs to scrape
    # This list will be the entry points to individual programme pages.
    # You'll likely scrape a main "all programmes" page first to get these links.
    programme_urls = [
        "https://www.aut.ac.nz/study/study-options/business/courses/bachelor-of-business",
        # Add more programme URLs here
        # "https://www.aut.ac.nz/study/study-options/art-design/courses/bachelor-of-design",
        # ...
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Set headless=False for visual debugging
        page = browser.new_page()

        for url in programme_urls:
            programme_data = scrape_university_programme(page, url)

            if programme_data:
                # Use programme_code as a unique identifier for upserting
                # If programme_code is not reliably available, use programme + university_name
                query = {"programme_code": programme_data.get("programme_code")}
                # Fallback if programme_code is missing or unreliable
                if not programme_data.get("programme_code"):
                    query = {"programme": programme_data.get("programme"), "link": programme_data.get("link")}
                
                # Check if the document already exists
                existing_doc = collection.find_one(query)

                if existing_doc:
                    # Update existing document
                    # Only update fields that might change, or use $set to replace the entire document content
                    # It's safer to use $set and explicitly list fields or replace the whole document
                    
                    # Option 1: Update specific fields using $set (more granular)
                    update_fields = programme_data.copy()
                    update_fields.pop("_id", None) # Remove _id if present from existing doc
                    update_fields["last_scraped_date"] = datetime.now() # Always update timestamp

                    collection.update_one(
                        query,
                        {"$set": update_fields}
                    )
                    print(f"Updated: {programme_data.get('programme')}")
                else:
                    # Insert new document
                    collection.insert_one(programme_data)
                    print(f"Inserted: {programme_data.get('programme')}")
            
            time.sleep(2) # Be polite, add a delay between requests

        browser.close()
        print("Scraping finished.")

if __name__ == "__main__":
    main_scraper()