# scrapes indeed.com for job listings and saves them to a csv file using pandas

import requests
from bs4 import BeautifulSoup
import pandas as pd

# get the raw html from each page and save it to a list
def get_raw_html(job_title='Data Scientist', location='New York', pages=10):
    raw_html_pages_list = []
    # indeed search page shows jobs 10 at a time, so we need to loop through all the pages*10
    for i in range(10, (pages*10)+1, 10):
        url = f'https://www.indeed.com/jobs?q={job_title}&l={location}&start={i}&vjk=b9dedd85514851bc"'
        response = requests.get(url)
        raw_html_pages_list.append(response.text)
    return raw_html_pages_list

# take in list of raw html pages, parse it for each job listing, and save it to a list 
def get_job_listings(raw_html_pages_list):
    list_of_jobs = []
    for raw_html in raw_html_pages_list:
        soup = BeautifulSoup(raw_html, 'lxml')
        job_listings = soup.find_all('a', class_='tapItem')
        for job in job_listings:
            list_of_jobs.append(job)
    return list_of_jobs

# get the list of jobs and extract the relevant information from each job listing in json format
def get_job_info(list_of_jobs):
    for job in list_of_jobs:
        jobs_container = job.find('table', class_='jobCardShelfContainer')
        last_active = jobs_container.find('span', class_='date').text
        if not '30+' in last_active:  # removes all jobs posted 30+ day ago
            job_snippet = jobs_container.find('div', class_='job-snippet')
            job_description = job_snippet.find('li').text.strip()
            position = job.find('h2', class_='jobTitle').text.strip()
            if position.startswith('new'):
                position = position[3:]
            company_info = job.find('div', class_='company_location')
            company_name = company_info.find('span', class_='companyName').text.strip()
            company_location = company_info.find('div', class_='companyLocation').text.strip()
            additional_info = job['href']
            yield {
                'a': position,
                'b': company_name,
                'c': company_location,
                'd': job_description,
                'e': f'https://www.indeed.com{additional_info}',
                # get the number from last_active
                'f': [int(s) for s in last_active.split() if s.isdigit()]
            }  
# save job info to a dataframe
def add_to_df(df, job_info):
    df_job_info = pd.DataFrame(job_info)
    df = df.merge(df_job_info, on='e', how='outer')
    return df

# save job info to a csv file
def save_to_csv(df):
    # drop empty columns from merge
    df = df.dropna(axis=1, how='all')
    # rename columns
    df.columns = ['position', 'company_name', 'company_location', 'job_description', 'additional_info', 'days_last_active']
    # save to csv
    df.to_csv('indeed_jobs.csv')

def main():
    # get user input
    job_title = input('Enter job title: ') or 'Data Scientist'
    location = input('Enter location: ') or 'New York'
    pages = input('Enter number of pages to scrape: ') or 10
    # get the raw html from each page and save it to a list
    raw_html_pages_list = get_raw_html(job_title, location, pages)
    # take in list of raw html pages, parse it for each job listing, and save it to a list 
    list_of_jobs = get_job_listings(raw_html_pages_list)
    # get the list of jobs and extract the relevant information from each job listing in json format
    job_info = get_job_info(list_of_jobs)
    # save job info to a dataframe
    df = pd.DataFrame(columns=['a', 'b', 'c', 'd', 'e', 'f'])
    df = add_to_df(df, job_info)
    # save job info to a csv file
    save_to_csv(df)

if __name__ == '__main__':
    main()
