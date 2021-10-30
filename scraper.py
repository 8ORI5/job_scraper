# scrapes indeed.com for job listings and saves them to a csv file using pandas

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_url(job_title='Data Scientist', location='New York'):
        response = requests.get(f"https://www.indeed.com/jobs?q={job_title}&l={location}&vjk=b9dedd85514851bc")
        return response.text

# get the links to the job listings from the raw text
def get_job_listings(html):
    soup = BeautifulSoup(html, 'lxml')
    jobs = soup.find_all('a', class_='tapItem')
    return jobs

# get the job info from each job listing page
def get_job_info(jobs):
    for index, job in enumerate(jobs):
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
                'position': position,
                'company_name': company_name,
                'company_location': company_location,
                'job_description': job_description,
                'additional_info': f'https://www.indeed.com{additional_info}',
                # get the number from last_active
                'last_active (days)': [int(s) for s in last_active.split() if s.isdigit()]
            }
def save_to_df(jobs):
    df = pd.DataFrame(jobs)
    return df

def add_to_df(df, jobs):
    df = df.append(jobs, ignore_index=True)
    return df

def save_to_csv(df):
    df = save_to_df(df)
    df.to_csv('jobs.csv', index=False)

def main():
    html = get_url(input('What kind of job are you looking for?: '), input('Where are you looking? : '))
    jobs = get_job_listings(html)
    jobs = list(get_job_info(jobs))
    save_to_csv(jobs)

if __name__ == '__main__':
    main()
