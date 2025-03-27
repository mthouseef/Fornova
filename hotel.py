import lxml.html
import json
import undetected_chromedriver as uc
import random
import time
import requests
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format of log messages
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)


today = datetime.today()
day = today.day
month = today.month
year = today.year
# Constants
region_to_extract = 1
limit_page = True
pages_to_extract = 2
BASE_URL = 'https://www.traveloka.com/en-th/hotel/thailand/'


def  get_deep_urls(BASE_URL):
    HEADERS_GET['user-agent'] = random.choice(user_agents)
    response = requests.get(BASE_URL, headers=HEADERS_GET,verify=False)
    
    dom = lxml.html.fromstring(response.text)
    script_content = dom.xpath("//script[@id='__NEXT_DATA__']//text()")
    json_val = json.loads(script_content[0])
    region_url_list = ["https://www.traveloka.com/en-th/hotel/"+url["path"] for url in json_val["props"]["pageProps"]["initialData"]["seoViewSearchList"]["geoChildren"]]
    deep_urls = []
    for region_url in region_url_list[:region_to_extract]:
        deep_urls += scrape_hotel_urls(region_url)
    return deep_urls






# Generate random User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

HEADERS_GET = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,kn;q=0.7,ja;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://www.traveloka.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-domain': 'accomRoom',
    'x-route-prefix': 'en-en',
}

def get_fresh_cookies(url):
    # Generate a random User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]
    random_user_agent = random.choice(user_agents)

    # Setup undetected ChromeDriver
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={random_user_agent}")
    options.add_argument("--lang=fr-FR")
    options.add_argument("--timezone=Europe/Paris")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-webrtc")
    options.add_argument("--disable-extensions")

    # Launch undetected Chrome
    driver = uc.Chrome(options=options)

    # Modify navigator properties
    driver.execute_script("""
        Object.defineProperty(navigator, 'language', { get: function() { return 'fr-FR'; } });
        Object.defineProperty(navigator, 'languages', { get: function() { return ['fr-FR', 'en-US']; } });
        Object.defineProperty(navigator, 'platform', { get: function() { return 'Win32'; } });
        Object.defineProperty(navigator, 'webdriver', { get: function() { return false; } });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: function() { return 8; } });
        Object.defineProperty(navigator, 'deviceMemory', { get: function() { return 8; } });
    """)

    # Clear cookies and cache
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.execute_script("indexedDB.deleteDatabase('WebRTC');")

    # Open the website
    #url = "https://www.traveloka.com"
    driver.get(url)

    # Wait to mimic human behavior
    time.sleep(random.uniform(3, 7))

    # Extract cookies
    cookies = driver.get_cookies()
    cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
    driver.close()
    driver.quit()
    return cookie_dict

def get_total_pages(response):
    """Calculate total number of pages based on number of hotels."""
    try:
        num_hotels = response.text.split(',"numHotels":"')[-1].split('",')[0]
        num_hotels = int(num_hotels)
    except:
        num_hotels = 0
    
    return (num_hotels // 10) if num_hotels else 1

def scrape_hotel_urls(region_url):
    """Scrape all hotel URLs from all pages with fresh cookies."""
    all_hotel_urls = []
    
    # Get fresh cookies for initial request
    HEADERS_GET['user-agent'] = random.choice(user_agents)
    response = requests.get(region_url, headers=HEADERS_GET,verify=False)
    
    dom = lxml.html.fromstring(response.text)
    total_pages = get_total_pages(response)
    logging.info(f"Total pages found: {total_pages}")

    if limit_page:
        logging.info(f"since you enable the limit the page so making page limit to :{pages_to_extract}")
        if total_pages > pages_to_extract:
            total_pages = pages_to_extract

    for page in range(1, total_pages + 1):
        url = region_url if page == 1 else f"{region_url}/{page}"
        logging.info(f"Scraping page {page}: {url}")
        
        # Get fresh cookies for each page
        HEADERS_GET['user-agent'] = random.choice(user_agents)
        response = requests.get(url, headers=HEADERS_GET,verify=False)
        
        dom = lxml.html.fromstring(response.text)
        script_content = dom.xpath("//script[@data-testid='popular_hotel_schema' and @type='application/ld+json']/text()")
        
        if script_content:
            json_data = json.loads(script_content[0].strip())
            hotel_urls = [item["item"]["url"] for item in json_data["itemListElement"]]
            all_hotel_urls.extend(hotel_urls)
        else:
            logging.info(f"No hotel data found on page {page}")
    
    logging.info(f"Total hotels collected: {len(all_hotel_urls)}")
    return all_hotel_urls

def format_price(amount, decimal_points=2):
    """Convert price string to float with specified decimal points."""
    return f"{float(amount) / (10 ** decimal_points):.{decimal_points}f}"

def get_post_res(fresh_cookies,json_data,hotel_url, max_retries=5):
    for attempt in range(max_retries):
        HEADERS_GET['user-agent'] = random.choice(user_agents)
        response = requests.post(
            'https://www.traveloka.com/api/v2/hotel/search/rooms',
            cookies=fresh_cookies,
            headers=HEADERS_GET,
            json=json_data,
            verify=False
        )
        
        if response.status_code == 200:
            return response.json(),fresh_cookies
        
        # Get fresh cookies if the request fails
        fresh_cookies = get_fresh_cookies(hotel_url)
        logging.info("fetched fresh cookies to process further")
        # Add a small delay before retrying
        time.sleep(2)  

    # If all retries fail, return None or raise an exception
    return None

def extract_rates(data, hotel_url):
    """Extract room rates from hotel data."""
    rates = []
    
    for room in data['data']['recommendedEntries']:
        room_id = room['hotelRoomId']
        room_name = room['name']
        
        for inventory in room['hotelRoomInventoryList']:
            rate = {'room_id': room_id}
            rate['Room_name'] = room_name
            rate['Rate_name'] = inventory['inventoryName']
            rate['Number of Guests'] = inventory['maxOccupancy']
            rate['Cancellation Policy'] = inventory['roomCancellationPolicy']['cancellationPolicyLabel']
            rate['Breakfast'] = inventory['isBreakfastIncluded']

            base_price = inventory['finalPrice']['totalPriceRateDisplay']['baseFare']['amount']
            final_price = inventory['finalPrice']['totalPriceRateDisplay']['totalFare']['amount']
            decimal_points = inventory['finalPrice']['totalPriceRateDisplay']['numOfDecimalPoint']

            rate['Price'] = format_price(base_price, int(decimal_points))
            rate['Currency'] = inventory['finalPrice']['totalPriceRateDisplay']['totalFare']['currency']
            rate['Total taxes'] = format_price(inventory['finalPrice']['totalPriceRateDisplay']['taxes']['amount'], int(decimal_points))
            rate['Total prices'] = format_price(final_price, int(decimal_points))
            
            if inventory['strikethroughDisplayFlag']:
                original_price = inventory['finalStrikethroughPrice']['totalPriceRateDisplay']['baseFare']['amount']
                total_price = inventory['finalStrikethroughPrice']['totalPriceRateDisplay']['totalFare']['amount']
                rate['original_price'] = format_price(original_price, int(decimal_points))
            
            rate['net_price_per_stay'] = format_price(final_price, int(decimal_points))
            rate['shown_price_per_stay'] = format_price(final_price, int(decimal_points))
            rate['total_price_per_stay'] = format_price(total_price, int(decimal_points))
            
            rates.append(rate)
    
    return rates

def fetch_room_details(hotel_urls):
    """Fetch and process room details for each hotel with fresh cookies."""
    all_hotels_data = []
    # Get fresh cookies for each hotel request
    fresh_cookies = get_fresh_cookies(BASE_URL)
    logging.info("Using Fresh Cookies:", fresh_cookies)
    for hotel_url in hotel_urls:  # Limiting to first 3 hotels
        hotel_id = hotel_url.split('/')[-1].split('-')[-1]
        logging.info(f"Fetching room details for hotel ID: {hotel_id}")
        
        json_data = {
            'fields': [],
            'data': {
                'contexts': {
                    'hotelDetailURL': hotel_url,
                    'bookingId': None,
                    'sourceIdentifier': 'HOTEL_DETAIL',
                    'shouldDisplayAllRooms': False,
                },
                'prevSearchId': 'undefined',
                'numInfants': 0,
                'ccGuaranteeOptions': {
                    'ccInfoPreferences': ['CC_TOKEN', 'CC_FULL_INFO'],
                    'ccGuaranteeRequirementOptions': ['CC_GUARANTEE'],
                },
                'rateTypes': ['PAY_NOW', 'PAY_AT_PROPERTY'],
                'isJustLogin': False,
                'isReschedule': False,
                'monitoringSpec': {
                    'referrer': '',
                    'isPriceFinderActive': 'null',
                    'dateIndicator': 'null',
                    'displayPrice': 'null',
                },
                'hotelId': hotel_id,
                'currency': 'THB',
                'labelContext': {},
                'isExtraBedIncluded': True,
                'hasPromoLabel': False,
                'supportedRoomHighlightTypes': ['ROOM'],
                'checkInDate': {'day': str(day), 'month': str(month), 'year': str(year)},
                'checkOutDate': {'day': str(day+1), 'month': str(month), 'year':  str(year)},
                'numOfNights': 1,
                'numAdults': 1,
                'numRooms': 1,
                'numChildren': 0,
                'childAges': [],
                'tid': 'edd0361c-dc0d-48ca-8f59-b6319d1ea05d',
            },
            'clientInterface': 'desktop',
        }
        
        data,fresh_cookies = get_post_res(fresh_cookies,json_data,hotel_url)
        if not data:
            fresh_cookies = get_fresh_cookies(hotel_url)
            continue
        else:
            try:
                hotel_data = {
                    'hotel_deeplink': hotel_url,
                    'hotel_id': hotel_id,
                    'rates': extract_rates(data, hotel_url)
                }
                all_hotels_data.append(hotel_data)
            except:
                fresh_cookies = get_fresh_cookies(hotel_url)
                continue
    
    # Save all data to JSON file
    with open('hotel_rates.json', 'w') as f:
        json.dump({'hotels': all_hotels_data}, f, indent=2)
    
    logging.info(f"Saved data for {len(all_hotels_data)} hotels to 'hotel_rates.json'")

if __name__ == "__main__":
    hotel_urls = get_deep_urls(BASE_URL)
    fetch_room_details(hotel_urls)
