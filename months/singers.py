from playwright.async_api import async_playwright

async def fetch_singers(payload):
    username = payload.get("username")
    password = payload.get("password")
    year = int(payload.get("year"))
    target_account = payload.get("target_account")

    if not username or not password or not target_account:
        raise ValueError("Required authentication details are missing")

    base_url = "https://www.last.fm/user/{}/library/artists?from={}-{:02d}-01&rangetype=1month&page=1"
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    singers = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto('https://www.last.fm/login')
            await page.fill('input[name="username_or_email"]', username)
            await page.fill('input[name="password"]', password)
            await page.click('button[name="submit"]')
            await page.wait_for_url(f'https://www.last.fm/user/{username}', timeout=30000)

            for month_index, month in enumerate(months, start=1):
                url = base_url.format(target_account, year, month_index)
                await page.goto(url)

                try:
                    await page.wait_for_selector('tbody[data-chart-date-range]', timeout=10000)
                    singer_row = page.locator('tbody[data-chart-date-range] > tr:first-child')
                    singer_name = await singer_row.locator('.chartlist-name a').get_attribute('title')
                    scrobbles = await singer_row.locator('.chartlist-bar .chartlist-count-bar-value').inner_text()
                    image_url = await singer_row.locator('.chartlist-image img').get_attribute('src')

                    if singer_name:
                        singers.append({
                            "month": month,
                            "singerName": singer_name,
                            "imageUrl": image_url if image_url else "",
                            "scrobbles": scrobbles if scrobbles else "0"
                        })

                except Exception as e:
                    print(f"Failed to fetch data for {month}: {e}")
                    singers.append({
                        "month": month,
                        "singerName": "",
                        "artist": "",
                        "imageUrl": "",
                        "scrobbles": ""
                    })

        except Exception as e:
            print(f"Failed during login or scraping: {e}")
        finally:
            await browser.close()

    return singers
