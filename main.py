import requests
import datetime
import schedule
import time
from playwright.sync_api import sync_playwright

url = "https://student-covid-screening.dsbn.org/api/vault/status/619e3b591ba66e0026463242"
headers = {
    "authorization": "",
    "user-agent": ""
}
uids = [354867442, 337352314]


def getval(request):
    if request.header_value("authorization") is not None:
        headers["authorization"] = request.header_value("authorization")
        print(headers)


def job():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://login.microsoftonline.com/?whr=dsbn.org')
        page.wait_for_load_state()
        page.fill('[placeholder="email@dsbn.org | loginid@students.dsbn.org"]', "bouffarn@students.dsbn.org")
        page.click('text="Next"')
        page.fill('[placeholder="Password"]', "cheeseandcrackersarereallygood555556")
        page.click('text="Sign in"')

        page.on('request', lambda request: getval(request))
        page.goto('https://student-covid-screening.dsbn.org/pass')
        page.locator('text="Go to school"').wait_for()
        browser.close()

    for user in uids:
        data = {
            "uid": user,
            "date": datetime.date.today(),
            "status": "passed"
        }
        response = requests.put(url=url, headers=headers, data=data)
        print(response)


schedule.every().day.at("07:00").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
