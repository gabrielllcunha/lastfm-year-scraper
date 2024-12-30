from playwright.async_api import async_playwright

async def fetch_songs(payload):
    username = payload.get("username")
    password = payload.get("password")
    year = int(payload.get("year"))
    target_account = payload.get("target_account")

    if not username or not password or not target_account:
        raise ValueError("Required authentication details are missing")

    base_url = "https://www.last.fm/user/{}/library/tracks?from={}-{:02d}-01&rangetype=1month&page=1"
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    songs = []

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
                    song_row = page.locator('tbody[data-chart-date-range] > tr:first-child')
                    song_name = await song_row.locator('.chartlist-name a').get_attribute('title')
                    artist_name = await song_row.locator('.chartlist-artist a').get_attribute('title')
                    scrobbles = await song_row.locator('.chartlist-bar .chartlist-count-bar-value').inner_text()
                    image_url = await song_row.locator('.chartlist-image img').get_attribute('src')

                    if song_name:
                        songs.append({
                            "month": month,
                            "name": song_name,
                            "artist": artist_name,
                            "imageUrl": image_url if image_url else "",
                            "scrobbles": scrobbles if scrobbles else "0"
                        })

                except Exception as e:
                    print(f"Failed to fetch data for {month}: {e}")
                    songs.append({
                        "month": month,
                        "name": "",
                        "artist": "",
                        "imageUrl": "",
                        "scrobbles": ""
                    })

        except Exception as e:
            print(f"Failed during login or scraping: {e}")
        finally:
            await browser.close()

    return songs
