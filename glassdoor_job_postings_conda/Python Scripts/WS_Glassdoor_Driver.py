"""
This script contains all the functions required to do webscraping. By importing this script, it allows me to scrape glassdoor job
postings for any job and location specified.

Using OOP concepts, I created a class called GlassdoorDriver, which is a descendant class of the selenium webdriver. Inside the
GlassdoorDriver class, I write all the methods required for scrapping glassdoor website specifically. Next, I have a global function
called scrape_job_role, which takes a job role string and a location string, and starts the scrapping process using the GlassdoorDriver
class. The function outputs the data collected as a .csv file, saving it into the current working directory.

Data collected for each job posting includes:

# 1. ID
# 2. Job Role
# 3. Location
# 4. Age
# 5. Job Description
# 6. Estimated Salary range
# 7. Estimation type (E.g. Estimated by employer or by glassdoor?)
# 8. Company Name
# 9. Company Average Total Rating
# 10. Proportion of reviewers that would recommend company to a friend
# 11. Company Average CareerOpportunities Rating
# 12. Company Average CompensationAndBenefits Rating
# 13. Company Average CultureAndValues Rating
# 14. Company Average SeniorManagement Rating
# 15. Company Average WorkLifeBalance Rating
# 16. Company Type (E.g. Private or Public)
# 17. Company Size
# 18. Company Sector
# 19. Company Industry
# 20. Company Year founded
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
import time
import os
from typing import Optional,List
from dotenv import find_dotenv,load_dotenv
import pandas as pd

driver_path = os.getcwd()+ "/chromedriver" #ChromeDriver needs to be in current working directory for the script to work
load_dotenv(find_dotenv()) #Need to create a dotenv file to store login details.
username_email = os.environ.get("USERNAME_EMAIL")
password = os.environ.get("PASSWORD")

class DriverImproved(webdriver.Chrome):
    #Include some methods to allow explicit waits
    def find_element_EW(self,by='id', value: Optional[str] = None, seconds = 60,type = "presence") -> webdriver.remote.webelement.WebElement:
        if type == "presence":
            element = WebDriverWait(self, seconds).until(EC.presence_of_element_located((by, value)))
        elif type == "clickable":
            element = WebDriverWait(self, seconds).until(EC.element_to_be_clickable((by,value)))
        return element
        
    def find_all_elements_EW(self,by='id', value: Optional[str] = None, seconds = 20) -> List[webdriver.remote.webelement.WebElement]:
        elements = WebDriverWait(self,seconds).until(EC.presence_of_all_elements_located((by,value)))
        return elements

# First, we create a class for glassdoor website. Using inspect on the website, we will design the methods of these classes
class GlassdoorDriver(DriverImproved):
    def __init__(self,driver_path,url):
        #The following code snippet for this __init__ method is taken directly from the following youtube video:
        #https://www.youtube.com/watch?v=LN1a0JoKlX8
        #Title: How to run Selenium Headless with Python | Python Headless Snippet | 2020
        #By Rajsuthan Official
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument(f'user-agent={user_agent}')
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--proxy-server='direct://'")
        self.options.add_argument("--proxy-bypass-list=*")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        #End of snippet taken from Rajsuthan Official
        super().__init__(service = ChromeService(executable_path=driver_path),options = self.options)
        self.implicitly_wait(10)
        self.get(url)
        self.job_search = None
        self.data = []
    
    def login(self):
        #Login into account
        time.sleep(1)
        self.find_element_EW(value = "SignInButton").click()
        self.find_element_EW(value = "modalUserEmail").send_keys(username_email,Keys.RETURN)
        self.find_element_EW(value = "modalUserPassword").send_keys(password,Keys.RETURN)

    def go_to_jobs(self):
        #Jobs Search
        time.sleep(3)
        link_buttons = self.find_element_EW(value = "ContentNav").find_elements(By.TAG_NAME,"li")
        jobs_button = list(filter(lambda e: e.get_attribute("data-test") == "site-header-jobs",link_buttons))[0]
        jobs_button.click()

    def search_job_role(self,job_role:str, location: str):
        #Search full-time job postings in singapore of the input job role and location
        for i in range(3):
            try:
                a_tag_items = self.find_element_EW(value = "app-navigation").find_elements(By.TAG_NAME,"a")
                search_button = list(filter(lambda e: e.get_attribute("data-test") == "jobs-search-results-page-link",a_tag_items))[0]
                search_button.click()
                time.sleep(3)
                break
            except Exception as e:
                if i != 2:
                    self.check_popups_and_try_to_close()
                    continue
                else:raise e

        #Job role
        for i in range(3):
            try:
                job_role_search_bar = self.find_element_EW(value = "searchBar-jobTitle")
                job_role_search_bar.clear()
                job_role_search_bar.send_keys(job_role)
                time.sleep(3)
                break
            except Exception as e:
                if i != 2:
                    self.check_popups_and_try_to_close()
                    continue
                else:raise e

        #location
        for i in range(3):
            try:
                location_search_bar = self.find_element_EW(value = "searchBar-location")
                #Use ctrl instead of command if using windows. I use macbook.
                ActionChains(self).move_to_element(location_search_bar).click()\
                    .key_down(Keys.COMMAND).send_keys("a",Keys.BACKSPACE).key_up(Keys.COMMAND).send_keys(location).perform()
                job_role_search_bar.send_keys(Keys.RETURN)
                break
            except Exception as e:
                if i != 2:continue
                else:raise e

        #Filter full-time
        for i in range(3):
            try:
                self.find_element_EW(value = "filter_jobType",type = "clickable").click()
                break
            except Exception as e:
                if i != 2:
                    self.check_popups_and_try_to_close()
                    continue
                else:raise e
        for i in range(3):
            try:
                button_elements = self.find_all_elements_EW(By.TAG_NAME,"button")
                full_time_jobs_button = list(filter(lambda e: e.get_attribute("value") == "fulltime",button_elements))[0]
                full_time_jobs_button.click()
                break
            except Exception as e:
                if i != 2:
                    self.check_popups_and_try_to_close()
                    time.sleep(2)
                    continue
                else:raise e

    def check_popups_and_try_to_close(self):
        #Check Job Alert
        try:
            job_alert_box = self.find_element(By.ID,"JAModal")
            close_button = job_alert_box.find_element(By.CLASS_NAME,"modal_closeIcon-svg")
            ActionChains(self).move_to_element(close_button).click().perform()
        except Exception as e:
            return None
    
    def get_page_numbers(self):
        #Gets current page and total number of pages of job posting
        page_sequence = self.find_element_EW(By.CLASS_NAME,"paginationFooter").text.split()
        return int(page_sequence[1]),int(page_sequence[3])
    
    def presence_next_page(self):
        #Checks if we there are still pages of job posting that we have not visited yet
        current_page,last_page = self.get_page_numbers()
        if current_page == last_page: return False
        else: return True

    
    def go_to_next_page_of_job_postings(self):
        #Goes to the next page of job postings
        try:
            self.find_element_EW(By.CLASS_NAME,value = "nextButton").click()
        except Exception as e:
            self.check_popups_and_try_to_close()
            time.sleep(5)
            self.find_element_EW(By.CLASS_NAME,value = "nextButton").click()

    def extract_data_from_current_job_posting(self):
        # Assume we have already click the job on the left hand side of the page.
        # Then, now we just have to look at the article on the right and extract information
        # Not all postings have the information we want. In those cases we will fill the value with None
        for i in range(3):
            try:
                #Getting article elements which contians most of the information we want
                jd_col_element = self.find_element_EW(value = "JDCol")
                try:
                    article_element = jd_col_element.find_element(By.TAG_NAME,"article")
                except Exception as e:
                    #Sometimes, article element cannot be found. In which case, we will need check which 
                    #of the 2 following scenarios are occuring:
                    
                    #Scenario 1: Error loading. (Solution is to reload)
                    try:
                        button_elements = jd_col_element.find_elements(By.TAG_NAME, "button")
                        retry_loading_button = list(filter(lambda x: x.text == "Retry your search",button_elements))[0]
                        retry_loading_button.click()
                        
                    #Scenario 2: Webpage is loading (Solution is to wait)
                    except:
                        time.sleep(5)
                    finally:
                        jd_col_element = self.find_element_EW(value = "JDCol")
                        article_element = jd_col_element.find_element(By.TAG_NAME,"article")
                ##

                job_id = article_element.get_attribute("data-id")
                job_name = self.find_element_EW(value = f"job-title-{job_id}").text
                job_location = self.find_element_EW(value = f"job-location-{job_id}").text
                company = self.find_element_EW(value = f"job-employer-{job_id}").text               
                job_age = self.find_element_EW(By.CLASS_NAME,"selected").find_element(By.CLASS_NAME,"listing-age").text
                job_posting_description = self.find_element_EW(value = f"JobDesc{job_id}").\
                    find_element(By.CLASS_NAME,"jobDescriptionContent").text
                
                #Salary
                try:
                    job_salary_range = self.find_element_EW(value = f"job-salary-{job_id}",seconds=5).text
                    job_salary_estimate_type = self.find_element_EW(value = f"job-salary-{job_id}",seconds=5).find_element(By.CLASS_NAME,"salary-estimate-type").text
                except Exception as E:
                    job_salary_range = None
                    job_salary_estimate_type = None

                #Company total rating
                try:
                    employer_stats_element = self.find_element_EW(value = "employerStats",seconds=5)
                    company_total_rating = list(filter(lambda x: x.get_attribute("data-test")=="rating-info", employer_stats_element.find_elements(By.CLASS_NAME,"e1pr2f4f1")))[0].text
                except:
                    company_total_rating = None

                #Proportion recommended to friend
                try:
                    employer_stats_element = self.find_element_EW(value = "employerStats",seconds=5)
                    proportion_reviewers_recommend_company = employer_stats_element.find_element(By.CLASS_NAME,"css-ztsow4").find_element(By.TAG_NAME,"text").text
                except:
                    proportion_reviewers_recommend_company = None

                #Company Individual Ratings
                try:
                    company_individual_ratings_element = article_element.find_element(By.CLASS_NAME,"erz4gkm0").find_elements(By.CLASS_NAME,"erz4gkm1")
                    company_individual_ratings = [e.text for e in company_individual_ratings_element]
                except:
                    company_individual_ratings = None

                #Company type/Size/Sector/Industry
                try:
                    def get_company_overview_info(company_overview_element):
                        temp = company_overview_element.find_elements(By.TAG_NAME,"span")
                        variable_name = temp[0].text
                        value = temp[1].text
                        return (variable_name,value)
                    company_overview_elements = self.find_element_EW(value = "EmpBasicInfo",seconds=5).find_elements(By.CLASS_NAME,"e1pvx6aw0")
                    overview_items = {variable_name:value for (variable_name,value) in [get_company_overview_info(i) for i in company_overview_elements]}
                    company_type_size_sector_industry_yearFounded = [overview_items.get("Type",None),\
                                                         overview_items.get("Size",None),\
                                                         overview_items.get("Sector",None),\
                                                         overview_items.get("Industry",None),\
                                                         overview_items.get("Founded",None)]
                except:
                    company_type_size_sector_industry_yearFounded = [None, None, None, None,None]

                self.data.append([job_id,job_name, job_location,job_age, job_posting_description,\
                       job_salary_range, job_salary_estimate_type, company,\
                       company_total_rating, proportion_reviewers_recommend_company, \
                       company_individual_ratings, company_type_size_sector_industry_yearFounded])
                break
            except Exception as e:

                if i != 2:
                    time.sleep(7.5)
                    continue
                else:
                    raise e

    def extract_job_posting_data_from_page(self):
        def get_postings_tabs():
            #This function returns a list of posting elements (left side of web page)
            for i in range(3):
                try:
                    left_column = self.find_element_EW(value = "MainCol")
                    posting_elements = left_column.find_elements(By.CLASS_NAME, "react-job-listing")
                    return posting_elements
                except Exception as e:
                    if i != 2: 
                        time.sleep(2)
                        continue
                    else: raise e
        
        def click_posting_tab(posting_number):
            #Clicks the specified posting element from left side of web page
            for k in range(3):
                try:
                    get_postings_tabs()[posting_number].click()
                    break
                except Exception as e:
                    if k != 2:
                        self.check_popups_and_try_to_close()
                        time.sleep(4)
                        continue
                    else: raise e

        number_of_postings = len(get_postings_tabs())

        for i in range(number_of_postings):

            click_posting_tab(i)

            for h in range(3):
                try:
                    self.extract_data_from_current_job_posting()
                    break
                except Exception as e:
                    if h != 2:
                        click_posting_tab(i) #kind of like refreshing
                        continue
                    else: raise e

    def scroll_to_view_page_number(self):
        #For debugging
        jd_col_element = self.find_element_EW(value = "JDCol")
        page_seq = self.find_element_EW(By.CLASS_NAME,"paginationFooter")
        ac = ActionChains(self).move_to_element(jd_col_element).scroll_to_element(page_seq)
        ac.perform()

def scrape_job_role(job_role: str, location: str) -> GlassdoorDriver:
    try:
        glassdoor_driver = GlassdoorDriver(driver_path,"https://www.glassdoor.com/")
        glassdoor_driver.job_search = job_role
        glassdoor_driver.login()
        print(f"Login successful for {job_role} search\n")
        glassdoor_driver.go_to_jobs()
        print(f"Go to jobs successful for {job_role} search\n")
        glassdoor_driver.search_job_role(job_role,location)
        print(f"Search Job role successful for {job_role} search\n")

        #Now, we cycle through the pages of the job postings.
        time.sleep(5)
        current_page_number, last_page_number = glassdoor_driver.get_page_numbers() #Indicates numbers of pages
        #1st Page
        try:
            glassdoor_driver.extract_job_posting_data_from_page()
            print(f"{job_role} : Page {current_page_number} of {last_page_number} extracted: PASSED\n")
        except Exception as e:
            print(f"{job_role} : Page {current_page_number} of {last_page_number} extracted: FAILED\n")
            raise e
        #Rest of the pages
        while glassdoor_driver.presence_next_page():
            try: 
                glassdoor_driver.go_to_next_page_of_job_postings()
                time.sleep(3)
                current_page_number, last_page_number = glassdoor_driver.get_page_numbers()
                glassdoor_driver.extract_job_posting_data_from_page()
                print(f"{job_role} : Page {current_page_number} of {last_page_number} extracted: PASSED\n")
            except Exception as e:
                print(f"{job_role} : Page {current_page_number} of {last_page_number} extracted: FAILED\n")
                glassdoor_driver.scroll_to_view_page_number()
                glassdoor_driver.get_screenshot_as_file(f"error_{job_role}.png") #Will help in debugging, by showing at which point, an error comes up
                raise e
        glassdoor_driver.scroll_to_view_page_number()
        glassdoor_driver.get_screenshot_as_file(f"passed_{job_role}.png")
    except Exception as e:
        glassdoor_driver.scroll_to_view_page_number()
        glassdoor_driver.get_screenshot_as_file(f"error_{job_role}.png") #Will help in debugging, by showing at which point, an error comes up
        raise e
    finally:
        #Export data collected into a csv
        df_column_names = ["job_id","job_name", "job_location","job_age", "job_posting_description",\
                       "job_salary_range", "job_salary_estimate_type", "company",\
                       "company_total_rating", "proportion_reviewers_recommend_company", \
                       "company_individual_ratings", "company_type_size_sector_industry_yearFounded"]
        df = pd.DataFrame(glassdoor_driver.data,columns=df_column_names)
        job_role_formated = job_role.replace(" ","_")
        df.to_csv(f"{os.getcwd()}/{job_role_formated}_extracted_data.csv")

        return glassdoor_driver

