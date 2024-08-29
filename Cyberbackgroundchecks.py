
import os


import json
import requests
import math
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import ast

def PhoneNumbersProcessing(phone_details_l):
    df = pd.DataFrame(phone_details_l)
    df['Year'] = df['Year'].astype(int)
    df = df.sort_values(by='Year', ascending=False)

    recent_landlines = df[df['Type'] == 'LandLine'].head(2)
    recent_mobiles = df[df['Type'] == 'Mobile'].head(3)

    result_df = pd.concat([recent_mobiles, recent_landlines]).reset_index(drop=True)
    result_dict = result_df.to_dict(orient='records')

    return result_dict

def Aging(soup):
    agedeceased = soup.find("div", {"class": "search-results__content"})
    if "deceased" in agedeceased.find("div", {"class": "card-header bg-white"}).text.replace("n", "").lower():
        return "Yes"
    else:
        return "No"

def GetPhoneDetails(soup):
    phone_details_l = []
    phonecard = soup.find_all("div", {"class": "col-md-12 text-secondary"})

    if len(phonecard) > 0:
        phonenumbers = phonecard[1].find_all("h3", {"class": "mb-0"})
        phonedetails = phonecard[1].find_all("p")

        for number, details in zip(phonenumbers, phonedetails):
            details = details.text.replace("n", "")
            temp = {}
            _type = ""
            if "landline" in details.lower():
                _type = "LandLine"

            elif "wireless" in details.lower():
                _type = "Mobile"

            temp["Number"] = number.text
            temp["Type"] = _type
            temp["Year"] = (details.split(" ")[-1])
            phone_details_l.append(temp)
    return phone_details_l

def GetEmails(soup):
    emails_l = []
    emailscard = soup.find_all("div", {"class": "col-md-12 text-secondary"})

    if len(emailscard) > 0:
        emails = emailscard[4].find_all("h3", {"class": "d-inline"})
        for email in emails:
            emails_l.append(email.text)

    return emails_l

def GetMainDetails(soup):
    maindetails_l = []
    cards = soup.find("div", {"class": "search-results__content"})

    for headerbar, url in zip(cards.find_all("div", {"class": "card-header bg-white"}), cards.find_all("div", {"class": "card-body pt-3 pb-0"})):
        temp = {}
        try:
            temp["Name"] = headerbar.find("span", {"class": "name-given"}).text.replace("n", "")
            temp["URL"] = url.find_all("div", {"class": "row"})[-1].find("div").find("a").get("href")
            maindetails_l.append(temp)
        except:
            pass

    return maindetails_l

def find_best_match(name_list, target_name):
    best_match, best_score, best_index = None, 0, -1
    for index, name in enumerate(name_list):
        name = name.lower()
        score = process.extractOne(target_name, [name])[1]
        if score > best_score:
            best_match, best_score, best_index = name, score, index

    return best_match, best_index

# Load the data
df = pd.read_csv("input.csv")
data_l = []

counter = 0
batch_size = 100  # Process in batches of 100 to avoid hitting rate limits
save_interval = 100  # Save intermediate results every 100 entries

for lastName, firstName, address, city, state in zip(df["Input Last Name"], df["Input First Name"], df["Owner Fix - Mailing Address"], df["Owner Fix - Mailing City"], df["Owner Fix - Mailing State"]):
    counter += 1
    inputName = str(firstName) + " " + str(lastName)

    # Sanitize the address to exclude anything after the # symbol
    if '#' in address:
        address = address.split('#')[0].strip()

    inputAddress = str(address).replace(" ", "-")
    inputCity = str(city).replace(" ", "-")

    temp = {}
    temp["Address"] = address  # Include the Address column
    temp["FirstName_Input"] = firstName
    temp["LastName_Input"] = lastName
    temp["Address_Input"] = address
    temp["City_Input"] = city
    temp["State_Input"] = state

    pageURL = ("https://cyberbackgroundchecks.com/address/" + str(inputAddress) + "/" + str(inputCity) + "/" + str(state)).lower()
    temp["Ping_URL"] = pageURL

    options = Options()
    # options.headless = True

    # service = FirefoxService(GeckoDriverManager().install())
    # driver1 = webdriver.Firefox(service=service, options=options)
    driver1 = webdriver.Chrome(options=options)

    driver1.maximize_window()
    sleep(2)

    driver1.get(pageURL)

    maindetails_l_1 = []
    sleep(2)

    try:
        resultsLabel = driver1.find_element(By.XPATH, "//h1[@class='total-records-label']")

        if resultsLabel:
            if "results" in resultsLabel.text:
                totalResults = int(resultsLabel.text.split(" ")[0])
                page_content = driver1.page_source

                print("Item No.", counter, ", Total Results Found:", totalResults)
                driver1.quit()

                pages = math.ceil(totalResults / 10)
                if totalResults < 10:
                    soup = bs(page_content, "html.parser")
                    MainDetails = GetMainDetails(soup)
                    maindetails_l_1.extend(MainDetails)

                else:
                    for i in range(1, pages + 1):
                        print("Getting Page No: ", i)
                        options = Options()
                        options.headless is True

                        service = FirefoxService(GeckoDriverManager().install())
                        driver = webdriver.Firefox(service=service, options=options)

                        driver.maximize_window()

                        driver.get(pageURL + "/" + str(i))
                        page_content = driver.page_source
                        soup = bs(page_content, "html.parser")
                        MainDetails = GetMainDetails(soup)
                        maindetails_l_1.extend(MainDetails)
                        driver.quit()

        names_l = []
        for mm in maindetails_l_1:
            names_l.append(mm["Name"])

        print("Getting Contact Details...!")

        target_name = inputName
        best_match, best_index = find_best_match(names_l, target_name.lower())

        options = Options()
        options.headless is True

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.maximize_window()
        driver.get("https://cyberbackgroundchecks.com" + maindetails_l_1[best_index]["URL"])
        page_content = driver.page_source
        soup = bs(page_content, "html.parser")

        driver.quit()

        deceasedORnot = Aging(soup)
        phonenumbers = GetPhoneDetails(soup)
        cleanedphonenumbers = PhoneNumbersProcessing(phonenumbers)
        emails = GetEmails(soup)
        temp["Is_Deceased"] = deceasedORnot
        temp["Phone"] = cleanedphonenumbers
        temp["Emails"] = str(", ".join(emails))
        temp["Profile_URL"] = str("https://cyberbackgroundchecks.com" + maindetails_l_1[best_index]["URL"])

        data_l.append(temp)

    except Exception as e:
        print(f"Error processing {inputName} at {address}, {city}, {state}: {e}")
        # Append the entry with blank fields for error cases
        temp["Ping_URL"] = ""
        temp["Is_Deceased"] = ""
        temp["Phone"] = []
        temp["Emails"] = ""
        temp["Profile_URL"] = ""
        data_l.append(temp)
        driver1.quit()

    # Save intermediate results every save_interval entries
    if counter % save_interval == 0:
        print(f"Saving intermediate results at {counter} entries.")
        df_intermediate = pd.DataFrame(data_l)
        df_intermediate.to_excel(f'enter your file path here', index=False)

# Save the last set of entries
if counter % save_interval != 0:
    print(f"Saving final entries at {counter} entries.")
    df_intermediate = pd.DataFrame(data_l)
    df_intermediate.to_excel(f"/Users/josebelfast-kum/Documents/output folder/Intermediate_Output_{counter}.xlsx", index=False)

# Combine all intermediate files and the final set into one DataFrame
all_dataframes = []
for i in range(save_interval, counter + save_interval, save_interval):
    try:
        df_temp = pd.read_excel(f"enter your file path here_Output_{i}.xlsx")
        all_dataframes.append(df_temp)
    except FileNotFoundError:
        pass

# Include the final entries that were not saved in an intermediate file
df_final_entries = pd.DataFrame(data_l)
all_dataframes.append(df_final_entries)

df_all_entries = pd.concat(all_dataframes, ignore_index=True)

# Post-processing to separate phone data into individual columns
def parse_phone_data(phone_str):
    try:
        phone_list = ast.literal_eval(phone_str)
        parsed_data = []
        for entry in phone_list:
            parsed_data.append((entry.get('Number', ''), entry.get('Type', ''), entry.get('Year', '')))
        while len(parsed_data) < 5:  # Ensure there are 5 sets
            parsed_data.append(('', '', ''))
        return parsed_data
    except:
        return [('', '', '')] * 5

# Apply the function to the Phone column
parsed_phone_data = df_all_entries['Phone'].apply(parse_phone_data)

# Create new columns in the DataFrame
for i in range(5):
    df_all_entries[f'Number{i+1}'] = parsed_phone_data.apply(lambda x: x[i][0])
    df_all_entries[f'Type{i+1}'] = parsed_phone_data.apply(lambda x: x[i][1])
    df_all_entries[f'Year{i+1}'] = parsed_phone_data.apply(lambda x: x[i][2])

# Drop the original Phone column
df_all_entries = df_all_entries.drop(columns=['Phone'])

# Save the processed data to a new Excel file
output_file_path = 'enter your file path here'
df_all_entries.to_excel(output_file_path, index=False)

print("Final data saved to", output_file_path)
