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
import os
import shutil




output_path = 'output'
papertype = "Exam Papers"
subject = input("Subject (case sensitive): ")
#subject = "Biology"
year = "2022"
exam = "Leaving Certificate"
searchterm = input("Search term: ")
#searchterm = "diagram"
numberofthreads = input("Number of threads (advanced setting, 2 is default):" )
if numberofthreads != None:
    semaphore = threading.BoundedSemaphore(value=int(numberofthreads))
else:
    semaphore = threading.BoundedSemaphore(value=4)

def delete_all_items(folder_path):
    items = os.listdir(folder_path)
    print(items)
    
    for item in items:
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path):
                # If it's a file, delete it
                os.remove(item_path)
                '''
            elif os.path.isdir(item_path):
                # If it's a directory, delete it and its contents recursively
                delete_all_items(item_path)
                '''
        except Exception as e:
            print(f"Error deleting {item_path}: {e}")
            

delete_all_items(output_path)

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
        #print(f"Page {page_number + 1}, Keyword Instances: {len(keyword_instances)}")

        if keyword_instances:
            # Print the type of keyword_instances[0]
            #print(type(keyword_instances[0]))

            # Get the Pixmap of the entire page
            pixmap = page.get_pixmap()

            # Write the Pixmap to a PNG file
            screenshot_path = f"{output_path}/{search_term}_in_{year}_page_{page_number + 1}.png"
            pixmap.save(screenshot_path)
            print(f"Screenshot saved at: {screenshot_path}")    

    pdf_document.close()


def SearchPage(subject, year):
    with semaphore:
        firefoxpath = 'D:\\Program Files\\Mozilla Firefox\\firefox.exe'
        chromepath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        url = 'https://www.examinations.ie/exammaterialarchive/'

        options = Options()
        options.binary = r'D:\Program Files\Mozilla Firefox\firefox.exe'

        # Set preferences directly in the options
        #options.profile = webdriver.FirefoxProfile()
        #options.add_argument("--headless=old")
        #options.add_argument('--disable-gpu')


        driver = webdriver.Chrome(options = options)
        driver.get(url)

        # First element (checkbox)
        checkbox_id = "MaterialArchive__noTable__cbv__AgreeCheck"
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, checkbox_id))
        )

        #print("Checkbox Element", checkbox.text)
        checkbox.click()

        # Second element (dropdown)
        dropdown_id = "MaterialArchive__noTable__sbv__ViewType"
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, dropdown_id))
        )
        #print("Dropdown Element", dropdown.text)

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

        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'viewerContainer')))

        pdf_url = driver.current_url

        pdf_content = download_pdf(pdf_url)

        driver.quit()

        # Save the PDF to a file (adjust file path as needed)
        pdf_path = "downloaded_pdf.pdf"
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content.getvalue())

        # Search and capture pages
        search_and_capture_page(pdf_path, searchterm, output_path, year)




threads = []
years = input("Years to search inclusive: (format example: 2017-2020): ")
yearbounds = years.split("-")
years_to_search = list()
for x in range((int(yearbounds[1])-int(yearbounds[0]))+1):
    years_to_search.append(int(yearbounds[0])+x) 

for targetyear in years_to_search:
    thread = threading.Thread(target=SearchPage, args=(subject, str(targetyear)))
    threads.append(thread)
    thread.start()
    time.sleep(20)

for thread in threads:
    thread.join()

print("All searches completed.")




        





