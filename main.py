import fake_headers
import bs4
import re
import json
import pprint

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

SKILL1 = 'Flask'
SKILL2 = 'Django'


def gen_headers():
    headers_gen = fake_headers.Headers(os="win", browser="chrome")
    return headers_gen.generate()


def wait_element(browser, delay_seconds=1, by=By.CLASS_NAME, value=None):
    return WebDriverWait(browser, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value)))


if __name__ == '__main__':
    URL = (f'https://spb.hh.ru/search/vacancy?text={SKILL1}+{SKILL2}'
           f'&area=1&area=2&hhtmFrom=resume_search_result&hhtmFromLabel=vacancy_search_line')

    path = ChromeDriverManager().install()
    browser_service = Service(executable_path=path)
    service = Service(executable_path=path)
    browser = Chrome(service=service)

    browser.get(URL)

    html_data = browser.page_source
    soup = bs4.BeautifulSoup(html_data, "lxml")

    page_count = int(soup.find('div', class_='pager').find_all('span', recursive=False)[-1].find('a').find('span').text)
    c = 1
    s = []
    for page in range(page_count):
        browser.get(url=f'{URL}&page={page}')
        job_page_tag = wait_element(browser, 5, By.CLASS_NAME, 'vacancy-serp-content')
        html_data = browser.page_source
        soup = bs4.BeautifulSoup(html_data, "lxml")
        job_list = soup.find_all('div', class_='serp-item serp-item_link')
        for job in job_list:
            job.find('a', class_='bloko-link')
            link = job.find('a', class_='bloko-link')['href']
            name = job.find('span', class_='serp-item__title serp-item__title-link').text
            salary = job.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary is not None:
                salary = salary.text.replace('\u202f', ' ').replace('\xa0', ' ')
            else:
                salary = 'з/п не указана'
            company = job.find('a', class_='bloko-link bloko-link_kind-tertiary').text.replace('\xa0', ' ')
            city = job.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text
            s.append({c: {'name': name,
                          'link': link,
                          'salary': salary,
                          'company': company,
                          'city': re.split(", ", city)[0]}})
            c += 1
    pprint.pprint(s)
    with open('hh.txt', 'w', encoding='utf-8') as file:
        json.dump(s, file, indent=4, ensure_ascii=False)

    with open('hh.txt', 'r', encoding='utf-8') as file:
        data = json.load(file)
        pprint.pprint(data)
