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
from queue import Queue


import time
import re
import threading
import os
import shutil




output_path = 'output'
papertype = "Exam Papers"
subject = input("Subject (case sensitive): ").strip()
#subject = "Biology"
year = "2022"
exam = "Leaving Certificate"
searchterm = input("Search term: ").strip()
linkstoclick = input("Which links should be clicked on? (0,2,3,4,5 (starts at 0)): ").strip()
#searchterm = "diagram"
numberoffetchthreads = input("Number of fetch threads (advanced setting, 2 is default):" ).strip()
numberofprocessthreads = input("Number of processing threads (advanced setting, 2 is default):" ).strip()

fetch_queue = Queue()

if numberoffetchthreads != "":
    print(f"threads = {numberoffetchthreads}")
    fetchsemaphore = threading.BoundedSemaphore(value=int(numberoffetchthreads))
else:
    print("threads = 2")
    fetchsemaphore = threading.BoundedSemaphore(value=2)

fetch_threads_complete = threading.Event()


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
def search_and_capture_page(pdf_path, search_term, output_path, year, index):
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
            screenshot_path = f"{output_path}/{search_term}_in_{year}_page_{page_number + 1}_{index}.png"
            pixmap.save(screenshot_path)
            print(f"Screenshot saved at: {screenshot_path}")    

    pdf_document.close()


def SearchPage(subject, year):
    with fetchsemaphore:
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

        td_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//td[@class='materialbody']"))
        )

        links = [int(link) for link in linkstoclick.split(",")]
        index = 0
        for td_element in td_elements:
            print(f"Content of td element: {td_element.text}")

            if "Click Here" in td_element.text:
                a_element = td_element.find_element(By.TAG_NAME, 'a')
                print(a_element.text)
                #a_element.click()
                print(index,links)

                if index in links:
                    a_element.click()
                    new_window = driver.window_handles[-1]
                    driver.switch_to.window(new_window)
                    pdf_url = driver.current_url
                    pdf_content = download_pdf(pdf_url)
                    driver.switch_to.window(driver.window_handles[0])

                    pdf_path = f"downloaded_pdf_{year}_{index}.pdf"
                    with open(pdf_path, 'wb') as pdf_file:
                        pdf_file.write(pdf_content.getvalue())
                     #Search and capture pages
                    search_and_capture_page(pdf_path, searchterm, output_path, year, index)
                index += 1

                   



        

        '''for td_element in td_elements:
            a_element = WebDriverWait(td_element, 10).until(
                EC.element_to_be_clickable((By.TAG_NAME, 'a'))
            )
            
            a_element = td_element.find_element(By.TAG_NAME, 'a')
            #print("link:", a_element.text)

            a_element.click()

            new_window = driver.window_handles[-1]
            driver.switch_to.window(new_window)

            driver.switch_to.window(driver.window_handles[0])'''

        '''links = linkstoclick.split(",")
        linkcounter = 0
        for td_element in td_elements:
            a_element = td_element.find_element(By.TAG_NAME, 'a')
            time.sleep(5)
            # Perform an action with a_element, for example, click
            if links.__contains__(linkcounter):
                
                a_element.click()
                time.sleep(5)

                new_window = driver.window_handles[-1]
                time.sleep(5)
                driver.switch_to.window(new_window)
                time.sleep(5)'''

        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'viewerContainer')))

        #pdf_url = driver.current_url

        #pdf_content = download_pdf(pdf_url)

        #driver.switch_to.window(driver.window_handles[0])

        # Save the PDF to a file (adjust file path as needed)
        




fetchthreads = []
processthreads = []
years = input("Years to search inclusive: (format example: 2017-2020): ")
yearbounds = years.split("-")
years_to_search = list()
for x in range((int(yearbounds[1])-int(yearbounds[0]))+1):
    years_to_search.append(int(yearbounds[0])+x) 

for targetyear in years_to_search:
    thread = threading.Thread(target=SearchPage, args=(subject, str(targetyear)))
    fetchthreads.append(thread)
    thread.start()
time.sleep(10)

#for year in years_to_search:
    #processingthread = threading.Thread(target = search_and_capture_page, args=(f"downloaded_pdf_{year}.pdf", searchterm, output_path, year))
    #processthreads.append(processingthread)
    #processingthread.start()

for thread in fetchthreads:
    thread.join()

#for thread in processthreads:
    #thread.join()

print("All searches completed.")




        





