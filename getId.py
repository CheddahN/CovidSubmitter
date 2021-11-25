import sys
from playwright.sync_api import sync_playwright

email = input("Enter your email: ")
password = input("Enter your password: ")
print("")


def getval(request):
    if 'https://student-covid-screening.dsbn.org/api/vault/status' in request.url and '?redirect' not in request.url:
        print(request.json()[0]['uid'])


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://login.microsoftonline.com/?whr=dsbn.org')
    page.wait_for_load_state()
    page.fill('[placeholder="email@dsbn.org | loginid@students.dsbn.org"]', email)
    page.click('text="Next"')
    page.fill('[placeholder="Password"]', password)
    page.click('text="Sign in"')

    page.on('response', lambda request: getval(request))
    page.goto('https://student-covid-screening.dsbn.org/pass')
    page.locator('text="Go to school"').wait_for()
    browser.close()
