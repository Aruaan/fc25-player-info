from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv


def scrape_futbin_players():
    url = "https://www.futbin.com/25/players?page=1"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    )

    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-height"))
        )
    except Exception as e:
        print(f"Timeout waiting for table: {e}")
        print("Page source at timeout:")
        print(BeautifulSoup(driver.page_source, "html.parser").prettify()[:1000])
        input("Press Enter after checking the browser...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
    else:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        input("Press Enter after table loads...")

    driver.quit()

    table = soup.find("table", class_="futbin-table players-table")
    if not table:
        print("Table not found in final source!")
        print(f"Final page snippet: {soup.prettify()[:500]}")
        return []

    players = []
    for row in table.find_all("tr")[1:10]:
        cols = row.find_all("td")
        if len(cols) > 5:
            name_col = cols[0]
            name = name_col.find("a", class_="player_name_players_table")
            if name:
                name = name.text.strip()
            else:
                name = name_col.text.strip().split("\n")[0]

            price_col = cols[3]
            price = price_col.text.strip().split()[0]
            players.append({"name": name, "price": price})

    return players


if __name__ == "__main__":
    player_data = scrape_futbin_players()
    for player in player_data:
        print(f"Name: {player['name']}, Price: {player['price']}")
