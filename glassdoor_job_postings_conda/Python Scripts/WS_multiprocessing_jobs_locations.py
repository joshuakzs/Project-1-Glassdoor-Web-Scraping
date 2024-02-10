"""
This script uses the WS_Glassdoor_Driver.py file (place that file in the same location as this file). As we have a lot of data to scrape, 
we need to find a way to increase efficiency. I do that by running the webscrapping in parallel using the multiprocessing library.

# The job roles that we will be searching data for includes:
# 1. Data Analyst
# 2. Machine Learning Engineer
# 3. Data Engineer
# 4. Database Administrator
# 5. Data Scientist
# 6. Data Architect
# 7. Software Engineer
# 8. Business Analyst
# 9. Statistician
"""

from WS_Glassdoor_Driver import *
import multiprocessing

# Looking at job roles from Singapore
if __name__ == '__main__':
    # My laptop has 8 cpu cores. Thus, we will only scrape up to 8 job roles at a time

    job_roles = ["Data Analyst","Machine Learning Engineer","Data Engineer","Database Administrator",\
                         "Data Scientist","Data Architect","Software Engineer","Business Analyst"]
    processes = [multiprocessing.Process(target = scrape_job_role, args = (job_role,"Singapore")) for \
                job_role in job_roles]
    for process in processes:
        process.start()
    for process in processes:
        process.join()

print("Completed scrapping")

# After running this script, edit job_roles variable, to include only remaining job role(s), including Statistician. 
# Then, run the script again.