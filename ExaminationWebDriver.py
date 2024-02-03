
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

outputpath = 'output'
papertype = "Exam Papers"
subject = "Biology"
year = "2022"
exam = "Leaving Certificate"
searchterm = "lipid"




def SearchPage(subject, year):

    firefoxpath = 'D:\\Program Files\\Mozilla Firefox\\firefox.exe'
    #geckodriver_path = 'D:\\Downloads\\geckodriver-v0.32.2-win64\\geckodriver.exe'
    url = 'https://www.examinations.ie/exammaterialarchive/'

    options = Options()
    options.binary_location = firefoxpath

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


    span_elements = set()
    iterations = 0
    original_span_elements = 0
    while True:
        wait = WebDriverWait(driver, 10)

        

        # Wait for the presence of the textLayer element
        text_layer = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'textLayer')))

        # Extract text from all spans within the textLayer
        spans = text_layer.find_elements(By.XPATH, '//span')
        
        current_span_elements = len(spans)
        
        time.sleep(.2)

        # Collect unique span texts in the set
        for span in spans:
            try:
                span_text = span.text.strip()
                if len(span_text) > 1:
                    #print(span_text)
                    span_elements.add(span_text)
            except StaleElementReferenceException:
            # Handle StaleElementReferenceException by continuing to the next iteration
                pass


        
        #print(spans)
        print(len(spans))
        
        # Break the loop if no more content is loaded
        if (original_span_elements == current_span_elements) and iterations > 2:
            print(original_span_elements)
            print(current_span_elements)
            break

        driver.find_element(by=By.TAG_NAME, value="body").send_keys(Keys.PAGE_DOWN * 5)
        iterations += 1

        original_span_elements = len(spans)


    # Print unique span texts
    #for span_text in span_elements:
        #print(span_text)
        




    # Wait for some time to allow content to load after scrolling
    time.sleep(.1)  # Adjust the sleep duration as needed

    all_text = " ".join(span_elements)
    sentences = re.split(r'\.+\s*', all_text)

    #driver.quit()
    
    return sentences


Search1page = SearchPage(subject, year)
for i, sentence in enumerate(Search1page):
    if searchterm in sentence:
        start_idx = max(0, i - 1)
        end_idx = min(len(Search1page), i + 1 + 1)
        context = Search1page[start_idx:end_idx]
        print(f"{year} Question + surrounding sentence: {' '.join(context)}")
        





