from playwright.async_api import async_playwright

async def fetch_albums(payload):
    username = payload.get("username")
    password = payload.get("password")
    year = int(payload.get("year"))
    target_account = payload.get("target_account")

    if not username or not password or not target_account:
        raise ValueError("Required authentication details are missing")

    base_url = "https://www.last.fm/user/{}/library/albums?from={}-{:02d}-01&rangetype=1month&page=1"
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    albums = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            await page.goto('https://www.last.fm/login')
            await page.fill('input[name="username_or_email"]', username)
            await page.fill('input[name="password"]', password)
            await page.click('button[name="submit"]')
            await page.wait_for_url(f'https://www.last.fm/user/{username}', timeout=60000)

            for month_index, month in enumerate(months, start=1):
                url = base_url.format(target_account, year, month_index)
                await page.goto(url, timeout=60000)

                try:
                    await page.wait_for_selector('tbody[data-chart-date-range]', timeout=10000)
                    album_row = page.locator('tbody[data-chart-date-range] > tr:first-child')
                    album_name = await album_row.locator('.chartlist-name a').get_attribute('title')
                    artist_name = await album_row.locator('.chartlist-artist a').get_attribute('title')
                    scrobbles = await album_row.locator('.chartlist-bar .chartlist-count-bar-value').inner_text()

                    album_link = await album_row.locator('.chartlist-name a').get_attribute('href')
                    full_album_url = f"https://www.last.fm{album_link}"
                    image_url = ""
                    if album_link:
                        await page.goto(full_album_url)

                        try:
                            cover_art_link = await page.locator('a.cover-art').get_attribute('href')
                            if cover_art_link:
                                cover_art_url = f"https://www.last.fm{cover_art_link}"
                                await page.goto(cover_art_url)
                                await page.wait_for_timeout(1000)
                                image_url = await page.locator('meta[property="og:image"]').get_attribute('content')

                        except Exception as e:
                            print(f"Failed to fetch high-res image for {month}: {e}")

                    if album_name:
                        albums.append({
                            "month": month,
                            "albumName": album_name,
                            "artist": artist_name,
                            "imageUrl": image_url if image_url else "",
                            "scrobbles": scrobbles if scrobbles else "0"
                        })

                except Exception as e:
                    print(f"Failed to fetch data for {month}: {e}")
                    albums.append({
                        "month": month,
                        "albumName": "",
                        "artist": "",
                        "imageUrl": "",
                        "scrobbles": ""
                    })

        except Exception as e:
            print(f"Failed during login or scraping: {e}")
        finally:
            await browser.close()
    print(albums)
    return albums
