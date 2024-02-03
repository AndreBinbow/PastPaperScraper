import fitz
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

import time
import re
import threading

output_path = 'output'
papertype = "Exam Papers"
subject = input("Subject: ")
year = "2022"
exam = "Leaving Certificate"
searchterm = input("Search term: ")

def download_pdf(url):
    response = requests.get(url)
    return BytesIO(response.content)

# Function to search for a term and capture the page
def search_and_capture_page(pdf_path, search_term, output_path, year):
    pdf_document = fitz.open(pdf_path)
    
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        keyword_instances = page.search_for(search_term)

        # Print the count of keyword instances on each page
        print(f"Page {page_number + 1}, Keyword Instances: {len(keyword_instances)}")

        if keyword_instances:
            # Print the type of keyword_instances[0]
            print(type(keyword_instances[0]))

            # Get the Pixmap of the entire page
            pixmap = page.get_pixmap()

            # Write the Pixmap to a PNG file
            screenshot_path = f"{output_path}/{year}_page_{page_number + 1}.png"
            pixmap.save(screenshot_path)
            print(f"Screenshot saved at: {screenshot_path}")    

    pdf_document.close()


def SearchPage(subject, year):

    firefoxpath = 'D:\\Program Files\\Mozilla Firefox\\firefox.exe'
    #geckodriver_path = 'D:\\Downloads\\geckodriver-v0.32.2-win64\\geckodriver.exe'
    url = 'https://www.examinations.ie/exammaterialarchive/'

    options = Options()
    options.binary_location = firefoxpath
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')

    driver = webdriver.Firefox()
    driver.get(url)

    # First element (checkbox)
    checkbox_id = "MaterialArchive__noTable__cbv__AgreeCheck"
    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, checkbox_id))
    )

    print("Checkbox Element", checkbox.text)
    checkbox.click()

    # Second element (dropdown)
    dropdown_id = "MaterialArchive__noTable__sbv__ViewType"
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, dropdown_id))
    )
    print("Dropdown Element", dropdown.text)

    # Use Select class to interact with the dropdown
    select = Select(dropdown)

    # Replace "Your Desired Option" with the actual text of the option you want to select
    select.select_by_visible_text(papertype)

    yeardropdown_id = "MaterialArchive__noTable__sbv__YearSelect"
    yeardropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, yeardropdown_id))
    )

    select = Select(yeardropdown)

    select.select_by_visible_text(year)

    examdropdown_id = "MaterialArchive__noTable__sbv__ExaminationSelect"
    examdropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, examdropdown_id))
    )

    select = Select(examdropdown)

    select.select_by_visible_text(exam)

    subjectdropdown_id = "MaterialArchive__noTable__sbv__SubjectSelect"
    subjectdropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, subjectdropdown_id))
    )

    select = Select(subjectdropdown)

    select.select_by_visible_text(subject)

    td_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//td[@class='materialbody'][2]"))
    )

    a_element = td_element.find_element(By.TAG_NAME, 'a')

    a_element.click()

    new_window = driver.window_handles[-1]
    driver.switch_to.window(new_window)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'viewerContainer')))

    pdf_url = driver.current_url
    
    pdf_content = download_pdf(pdf_url)

    driver.quit()

    # Save the PDF to a file (adjust file path as needed)
    pdf_path = "downloaded_pdf.pdf"
    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(pdf_content.getvalue())

    # Search and capture pages
    search_and_capture_page(pdf_path, searchterm, output_path, year)

    

SearchPage(subject, year)



        





