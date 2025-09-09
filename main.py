import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
from typing import List, Dict, Optional

class OLXScraper:
    def __init__(self):
        self.base_url = "https://www.olx.pl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def scrape_url(self, url: str, max_pages: int = 10) -> List[Dict]:
        """
        Scrape listings from a specific OLX URL
        
        Args:
            url: The OLX URL to scrape
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of listing dictionaries
        """
        listings = []
        
        for page in range(1, max_pages + 1):
            print(f"\n--- Scraping page {page} ---")
            
            # Add page parameter to URL
            page_url = f"{url}&page={page}" if '?' in url else f"{url}?page={page}"
            page_listings = self._scrape_listings_page(page_url)
            
            if not page_listings:
                print(f"No listings found on page {page}, stopping...")
                break
                
            # Filter out invalid listings
            valid_listings = [l for l in page_listings if l.get('title') != 'N/A' and l.get('url')]
            listings.extend(valid_listings)
            
            print(f"Page {page}: Found {len(page_listings)} total, {len(valid_listings)} valid listings")
            print(f"Total valid listings so far: {len(listings)}")
            
            # Longer delay to avoid rate limiting
            time.sleep(2)
        
        return listings

    def scrape_url_detailed(self, url: str, max_pages: int = 10, max_detailed: int = 50) -> List[Dict]:
        """
        Scrape listings with detailed information from a specific OLX URL
        
        Args:
            url: The OLX URL to scrape
            max_pages: Maximum number of pages to scrape
            max_detailed: Maximum number of listings to get detailed info for
        
        Returns:
            List of detailed listing dictionaries
        """
        # First get basic listings
        basic_listings = self.scrape_url(url, max_pages)
        
        if not basic_listings:
            return []
        
        print(f"\n--- Getting detailed information for {min(max_detailed, len(basic_listings))} listings ---")
        
        detailed_listings = []
        for i, listing in enumerate(basic_listings[:max_detailed]):
            if not listing.get('url'):
                continue
                
            print(f"Getting details for listing {i+1}/{min(max_detailed, len(basic_listings))}: {listing.get('title', 'N/A')[:50]}...")
            
            try:
                details = self.get_listing_details(listing['url'])
                # Merge basic info with detailed info
                detailed_listing = {**listing, **details}
                detailed_listings.append(detailed_listing)
                
                # Respectful delay
                time.sleep(3)
                
            except Exception as e:
                print(f"Error getting details for listing {i+1}: {e}")
                # Still add the basic listing info
                detailed_listings.append(listing)
                continue
        
        return detailed_listings

    def search_listings(self, query: str, location: str = "", max_pages: int = 5) -> List[Dict]:
        """
        Search for listings on OLX.pl
        
        Args:
            query: Search term
            location: Location filter (optional)
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of listing dictionaries
        """
        listings = []
        
        # Build search URL
        search_url = f"{self.base_url}/oferty/q-{query}/"
        if location:
            search_url += f"{location}/"
        
        for page in range(1, max_pages + 1):
            page_url = f"{search_url}?page={page}"
            page_listings = self._scrape_listings_page(page_url)
            
            if not page_listings:
                break
                
            listings.extend(page_listings)
            time.sleep(1)  # Be respectful to the server
        
        return listings

    def _scrape_listings_page(self, url: str) -> List[Dict]:
        """Scrape a single page of listings with improved selectors"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: save HTML to file to inspect structure (only for first page)
            if 'page=1' in url or 'page=' not in url:
                with open(f'debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                print("HTML saved to debug_page.html for inspection")
            
            listings = []
            
            # Try multiple selectors for listing containers
            selectors = [
                '[data-cy="l-card"]',
                '[data-testid="l-card"]', 
                'div[data-cy="l-card"]',
                '.css-1sw7q4x',  # Common OLX class
                '[data-cy="listing-ad-title"]',
                '.offer-wrapper',
                'article',
                'div[class*="listing"]',
            ]
            
            listing_containers = []
            for selector in selectors:
                containers = soup.select(selector)
                if containers:
                    print(f"Found {len(containers)} containers with selector: {selector}")
                    listing_containers = containers
                    break
            
            if not listing_containers:
                print("No listing containers found with any selector")
                # Try to find any divs that might contain listings
                all_divs = soup.find_all('div')
                print(f"Total divs found: {len(all_divs)}")
                
                # Look for divs with links and text that might be listings
                potential_listings = []
                for div in all_divs:
                    if div.find('a') and (div.find('h3') or div.find('h4') or div.find('h6')):
                        potential_listings.append(div)
                
                print(f"Found {len(potential_listings)} potential listing divs")
                listing_containers = potential_listings[:50]  # Take first 50 to avoid too many
            
            for i, container in enumerate(listing_containers):
                try:
                    listing_data = self._extract_listing_data_improved(container)
                    if listing_data:
                        listings.append(listing_data)
                        if i < 3:  # Debug first 3 listings
                            print(f"Listing {i+1}: {listing_data.get('title', 'N/A')[:50]}...")
                except Exception as e:
                    print(f"Error extracting listing {i+1}: {e}")
                    continue
            
            print(f"Successfully extracted {len(listings)} listings from page")
            return listings
            
        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error for {url}: {e}")
            return []

    def _extract_listing_data_improved(self, container) -> Optional[Dict]:
        """Extract data with improved selectors and multiple fallbacks"""
        try:
            # Title - try multiple selectors
            title = "N/A"
            title_selectors = [
                'h3', 'h4', 'h6',
                '[data-cy="listing-ad-title"]',
                '[data-testid="listing-ad-title"]',
                '.css-16v5mdi h6',
                'a h6', 'a h4', 'a h3',
                '.title', '.offer-item-title',
            ]
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                    break
            
            # URL - try multiple approaches
            url = ""
            link_elem = container.find('a', href=True)
            if link_elem:
                relative_url = link_elem.get('href')
                if relative_url:
                    if relative_url.startswith('http'):
                        url = relative_url
                    else:
                        url = urljoin(self.base_url, relative_url)
            
            # Price - try multiple selectors
            price = "N/A"
            price_selectors = [
                '[data-testid="ad-price"]',
                '.price', '.css-10b0gli', '.css-1uwck7i',
                'p[data-testid="ad-price"]',
                'span[data-testid="ad-price"]',
                'strong', 'b',  # Price often in bold
            ]
            
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if 'zł' in price_text or price_text.replace(' ', '').replace(',', '').replace('.', '').isdigit():
                        price = price_text
                        break
            
            # Location and date
            location = "N/A"
            date = "N/A"
            
            location_selectors = [
                '[data-testid="location-date"]',
                '.css-veheph', '.location', '.css-1a4brun',
            ]
            
            for selector in location_selectors:
                location_elem = container.select_one(selector)
                if location_elem:
                    location_text = location_elem.get_text(strip=True)
                    if location_text:
                        # Try to split location and date
                        parts = location_text.split(' - ')
                        if len(parts) >= 2:
                            location = parts[0]
                            date = parts[-1]
                        else:
                            location = location_text
                        break
            
            # Image
            image_url = ""
            img_elem = container.find('img')
            if img_elem:
                image_url = img_elem.get('src', '') or img_elem.get('data-src', '')
            
            # Extract ID from URL
            listing_id = self._extract_id_from_url(url)
            
            # Only return if we have at least a title or URL
            if title != "N/A" or url:
                return {
                    'id': listing_id,
                    'title': title,
                    'price': price,
                    'location': location,
                    'date': date,
                    'url': url,
                    'image_url': image_url
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting listing data: {e}")
            return None

    def _extract_id_from_url(self, url: str) -> str:
        """Extract listing ID from URL"""
        try:
            # OLX URLs typically end with ID-*.html or ID*.html
            match = re.search(r'ID([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
            
            # Alternative pattern
            match = re.search(r'-([a-zA-Z0-9]+)\.html', url)
            if match:
                return match.group(1)
                
            return ""
        except:
            return ""

    def get_listing_details(self, listing_url: str) -> Dict:
        """Get detailed information for a specific listing"""
        try:
            response = self.session.get(listing_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed information with multiple selectors
            details = {
                'detailed_title': self._get_text_by_multiple_selectors(soup, [
                    'h1', '[data-cy="ad_title"]', '.css-r9zjja-Text'
                ]),
                'detailed_price': self._get_text_by_multiple_selectors(soup, [
                    '[data-testid="ad-price-container"]', 
                    '.css-8gi6ch', 
                    '.css-1uwck7i',
                    'h3[data-testid="ad-price-container"]'
                ]),
                'description': self._get_text_by_multiple_selectors(soup, [
                    '[data-cy="ad_description"]',
                    '.css-g5mtl5-Text',
                    '.offer-description',
                    '.description'
                ]),
                'detailed_location': self._get_text_by_multiple_selectors(soup, [
                    '[data-testid="location-date"]',
                    '.css-veheph',
                    '.location-date'
                ]),
                'seller_name': self._get_text_by_multiple_selectors(soup, [
                    '[data-testid="seller-name"]',
                    '.css-1cxvtlc',
                    '.seller-name'
                ]),
                'seller_type': self._get_text_by_multiple_selectors(soup, [
                    '[data-testid="seller-type"]',
                    '.css-12hdxwj'
                ]),
                'phone_number': self._extract_phone_number(soup),
                'images': self._extract_images(soup),
                'attributes': self._extract_attributes(soup),
                'posted_date': self._extract_posted_date(soup),
                'viewed_count': self._extract_view_count(soup),
                'safety_tips': self._extract_safety_tips(soup),
                'listing_features': self._extract_listing_features(soup)
            }
            
            return details
            
        except requests.RequestException as e:
            print(f"Error getting listing details: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error getting listing details: {e}")
            return {}

    def _get_text_by_multiple_selectors(self, soup, selectors: List[str]) -> str:
        """Try multiple CSS selectors to get text"""
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text:
                    return text
        return "N/A"

    def _get_text_by_selector(self, soup, selector: str) -> str:
        """Helper method to get text by CSS selector"""
        elem = soup.select_one(selector)
        return elem.get_text(strip=True) if elem else "N/A"

    def _extract_phone_number(self, soup) -> str:
        """Extract phone number if available"""
        phone_selectors = [
            '[data-testid="contact-phone"]',
            '.css-1p6wsjo',
            'a[href*="tel:"]'
        ]
        
        for selector in phone_selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'a' and elem.get('href'):
                    return elem.get('href').replace('tel:', '')
                return elem.get_text(strip=True)
        
        return "N/A"

    def _extract_images(self, soup) -> List[str]:
        """Extract all image URLs from listing"""
        images = []
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            src = img.get('src', '') or img.get('data-src', '')
            if src and any(domain in src for domain in ['static.olx', 'apollo', 'img.olx']):
                # Clean up image URL
                if src.startswith('//'):
                    src = 'https:' + src
                images.append(src)
        
        return list(set(images))  # Remove duplicates

    def _extract_attributes(self, soup) -> Dict[str, str]:
        """Extract listing attributes/parameters"""
        attributes = {}
        
        # Try multiple selectors for parameters
        param_selectors = [
            'li[class*="css-"]',
            '.params li',
            '.offer-params li',
            '.css-1h1vnm6',
        ]
        
        for selector in param_selectors:
            param_containers = soup.select(selector)
            if param_containers:
                for container in param_containers:
                    text = container.get_text(strip=True)
                    if ':' in text:
                        key, value = text.split(':', 1)
                        attributes[key.strip()] = value.strip()
                break
        
        return attributes

    def _extract_posted_date(self, soup) -> str:
        """Extract when the listing was posted"""
        date_selectors = [
            '[data-testid="location-date"]',
            '.css-veheph',
            '.offer-meta'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text()
                # Look for date patterns
                date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})|(\d+ \w+ temu)|(dzisiaj|wczoraj)', text)
                if date_match:
                    return date_match.group(0)
        
        return "N/A"

    def _extract_view_count(self, soup) -> str:
        """Extract view count if available"""
        view_selectors = [
            '[data-testid="ad-view-count"]',
            '.css-1h8ojeu',
            '.views'
        ]
        
        for selector in view_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if any(word in text.lower() for word in ['wyświetl', 'view', 'obejrz']):
                    return text
        
        return "N/A"

    def _extract_safety_tips(self, soup) -> List[str]:
        """Extract safety tips if available"""
        safety_tips = []
        safety_selectors = [
            '.safety-tips li',
            '[data-testid="safety-tip"]'
        ]
        
        for selector in safety_selectors:
            elements = soup.select(selector)
            for elem in elements:
                tip = elem.get_text(strip=True)
                if tip:
                    safety_tips.append(tip)
        
        return safety_tips

    def _extract_listing_features(self, soup) -> List[str]:
        """Extract listing features/highlights"""
        features = []
        
        # Look for feature badges or highlights
        feature_selectors = [
            '.badge',
            '.highlight',
            '.feature',
            '[data-testid="ad-highlight"]'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for elem in elements:
                feature = elem.get_text(strip=True)
                if feature and len(feature) < 100:  # Avoid long text
                    features.append(feature)
        
        return list(set(features))  # Remove duplicates

    def save_to_json(self, data: List[Dict], filename: str = 'olx_listings.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")

# Example usage
def main():
    scraper = OLXScraper()
    
    # Scrape the specific parking/garage URL
    parking_url = "https://www.olx.pl/nieruchomosci/garaze-parkingi/wynajem/warszawa/?search%5Bphotos%5D=1&search%5Border%5D=created_at:desc"
    
    print("=== BASIC SCRAPING (TARGET: 300 RECORDS) ===")
    
    # Start with more pages to ensure we get 300 records
    target_records = 300
    max_pages = 50  # Increase max pages significantly
    
    listings = scraper.scrape_url(parking_url, max_pages=max_pages)
    
    # If we don't have enough, try without photo filter to get more results
    if len(listings) < target_records:
        print(f"\nOnly found {len(listings)} listings with photos. Trying without photo filter...")
        backup_url = "https://www.olx.pl/nieruchomosci/garaze-parkingi/wynajem/warszawa/?search%5Bphotos%5D=1&search%5Border%5D=created_at:desc"
        additional_listings = scraper.scrape_url(backup_url, max_pages=30)
        
        # Combine and deduplicate by URL
        all_listings = listings.copy()
        existing_urls = {listing['url'] for listing in listings}
        
        for listing in additional_listings:
            if listing['url'] not in existing_urls:
                all_listings.append(listing)
                existing_urls.add(listing['url'])
                if len(all_listings) >= target_records:
                    break
        
        listings = all_listings
    
    # Trim to exactly 300 if we have more
    if len(listings) > target_records:
        listings = listings[:target_records]
    
    print(f"Found {len(listings)} basic parking/garage listings")
    
    # Save basic listings
    scraper.save_to_json(listings, 'parking_listings_basic_300.json')
    
    print("\n=== DETAILED SCRAPING ===")
    # Get detailed information for first 100 listings (adjust as needed)
    detailed_count = min(100, len(listings))  # Get details for up to 100 listings
    
    detailed_listings = []
    print(f"Getting detailed information for {detailed_count} listings...")
    
    for i, listing in enumerate(listings[:detailed_count]):
        if not listing.get('url'):
            continue
            
        print(f"Getting details for listing {i+1}/{detailed_count}: {listing.get('title', 'N/A')[:50]}...")
        
        try:
            details = scraper.get_listing_details(listing['url'])
            # Merge basic info with detailed info
            detailed_listing = {**listing, **details}
            detailed_listings.append(detailed_listing)
            
            # Respectful delay
            time.sleep(3)
            
        except Exception as e:
            print(f"Error getting details for listing {i+1}: {e}")
            # Still add the basic listing info
            detailed_listings.append(listing)
            continue
    
    print(f"Found {len(detailed_listings)} detailed parking/garage listings")
    
    # Save detailed listings
    scraper.save_to_json(detailed_listings, 'parking_listings_detailed_300.json')
    
    # Print summary
    if listings:
        print(f"\n=== SUMMARY ===")
        print(f"Target records: {target_records}")
        print(f"Basic listings: {len(listings)}")
        print(f"Detailed listings: {len(detailed_listings)}")
        print(f"Listings with valid titles: {sum(1 for l in listings if l['title'] != 'N/A')}")
        print(f"Listings with valid URLs: {sum(1 for l in listings if l['url'])}")
        print(f"Listings with prices: {sum(1 for l in listings if l['price'] != 'N/A')}")
        
        # Show price distribution
        prices_with_values = [l['price'] for l in listings if l['price'] != 'N/A']
        print(f"Listings with price information: {len(prices_with_values)}")
        
        print("\nSample basic listing:")
        print(json.dumps(listings[0], indent=2, ensure_ascii=False))
        
        if detailed_listings:
            print("\nSample detailed listing keys:")
            print(list(detailed_listings[0].keys()))
            
        print(f"\n=== FILES CREATED ===")
        print(f"- parking_listings_basic_300.json ({len(listings)} records)")
        print(f"- parking_listings_detailed_300.json ({len(detailed_listings)} records)")

if __name__ == "__main__":
    main()