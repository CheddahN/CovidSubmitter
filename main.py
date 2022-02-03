import asyncio
import json
import discord
from colorama import Fore, Back, Style
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

try:
    with open('data.json') as file:
        data = json.load(file)
except:
    data = {"token": input("Please enter your bot token: "),
            "prefix": "]",
            "users": {

            }}
    with open('data.json', 'w') as file:
        json.dump(data, file)

client = discord.Client()


async def login(email, password, test):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://login.microsoftonline.com/?whr=dsbn.org')
        await page.wait_for_load_state()
        await page.fill('[placeholder="email@dsbn.org | loginid@students.dsbn.org"]', email)
        await page.click('text="Next"')
        try:
            await page.fill(selector='[placeholder="Password"]', value=password, timeout=3000)
        except:
            return False
        await page.click('text="Sign in"')
        if test:
            try:
                await page.wait_for_url('https://www.office.com/**', timeout=60000.00)
                return True
            except:
                return False
        else:
            await page.goto('https://student-covid-screening.dsbn.org/simple')
            await page.click('text="Take the School and Child Care Screening Online"')
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/**')
            await page.click('text="Start school screening"')
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/vaccinated')
            await page.click("button:has-text(\"No\")")
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/travel')
            await page.click("button:has-text(\"No\")")
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/symptoms')
            await page.check("input[name=\"none_of_the_above\"]")
            await page.click('text="Continue"')
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/covid-positive')
            await page.click("button:has-text(\"No\")")
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/household-isolation')
            await page.click("button:has-text(\"No\")")
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/doctor-self-isolate')
            await page.click("button:has-text(\"No\")")
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/contact')
            await page.click("button:has-text(\"No\")")
            await page.wait_for_url('https://covid-19.ontario.ca/school-screening/approved')
            await asyncio.sleep(3)
            await browser.close()
            return True


@client.event
async def on_message(message):
    channel = message.author
    if message.author == client.user:
        return
    if message.content.startswith(data['prefix'] + 'help'):
        await message.author.send('```' +
                                  data['prefix'] + "add    | Add yourself from the database\n" +
                                  data['prefix'] + "check  | Check to see if you're in the database\n" +
                                  data['prefix'] + "remove | Remove yourself from the database"
                                  + "```")
    elif message.content.startswith(data['prefix'] + 'add'):
        print(message.author.id)

        def check(m):
            return m.author == channel

        await channel.send("Please send your email")
        email = await client.wait_for('message', check=check)
        await channel.send("Please send your password")
        password = await client.wait_for('message', check=check)
        async with channel.typing():
            result = await login(email=email.content, password=password.content, test=True)
            if result:
                data['users'][str(channel.id)] = {"email": email.content, "password": password.content}
                with open('data.json', 'w') as file:
                    json.dump(data, file)
                await channel.send('Successfully added ' + email.content + ' to the list')
                print("Added " + email.content + " from " + str(channel.id))
            else:
                await channel.send('An error occurred, check your spelling or try again later')
    elif message.content.startswith(data['prefix'] + 'check'):
        if str(channel.id) in data['users']:
            await channel.send('Your account has ' + data['users'][str(channel.id)]['email'] + ' in the list')
        else:
            await channel.send('Your account has no email in the list')
    elif message.content.startswith(data['prefix'] + 'remove'):
        if str(channel.id) in data['users']:
            await channel.send(data['users'][str(channel.id)]['email'] + ' has been removed from the list')
            del data['users'][str(channel.id)]
            with open('data.json', 'w') as file:
                json.dump(data, file)
        else:
            await channel.send('Your account already has no email in the list')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(data['prefix'] + 'help'))
    print('Logged in as ' + client.user.name)


async def job():
    while True:
        hour = 7
        minute = 10
        await client.wait_until_ready()
        now = datetime.now()
        future = datetime(now.year, now.month, now.day, hour, minute)
        if future.time() <= now.time():
            future += timedelta(days=1)
        print(f"{Fore.YELLOW}Next run " + str(future) + " in " + str((future - now).total_seconds()) + " seconds"+ Fore.RESET)
        await asyncio.sleep((future - now).total_seconds())

        for user in data['users']:
            response = await login(email=data['users'][user]['email'], password=data['users'][user]['password'], test=False)
            print(Fore.BLUE + data['users'][user]['email'] + " success " + str(response) + Fore.RESET)

client.loop.create_task(job())
client.run(data['token'])
