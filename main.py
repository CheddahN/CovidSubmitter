import json
import schedule
import time
from playwright.sync_api import sync_playwright

file = json.load(open('data.json'))
url = 'https://student-covid-screening.dsbn.org/api/vault/status/619e3b591ba66e0026463242'
headers = {
    'authorization': "",
    'user-agent': ""
}


def job():
    for user in file['users']:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://login.microsoftonline.com/?whr=dsbn.org')
            page.wait_for_load_state()
            page.fill('[placeholder="email@dsbn.org | loginid@students.dsbn.org"]', file['users'][user]['email'])
            page.click('text="Next"')
            page.fill('[placeholder="Password"]', file['users'][user]['password'])
            page.click('text="Sign in"')

            page.goto('https://student-covid-screening.dsbn.org/pass')
            page.locator('text="Go to school"').wait_for()
            browser.close()
            print("seccess " + user)


schedule.every().day.at('06:20').do(job)
job()
while True:
    schedule.run_pending()
    time.sleep(1)
