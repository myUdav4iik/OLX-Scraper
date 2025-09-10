# OLX Parking Spots Scraper

A comprehensive web scraper for extracting parking and garage listings from OLX.pl with both graphical and command-line interfaces.

## Features

- **Dual Interface**: Both GUI and command-line options
- **Smart Scraping**: Extracts basic and detailed listing information
- **Progress Tracking**: Real-time progress updates and statistics
- **Customizable**: Configure pages, records, and output settings
- **Respectful**: Built-in delays to avoid overwhelming the server
- **Export Options**: Save data as JSON files with timestamps

## Requirements

- Python 3.7+
- Required packages (install via `pip install -r requirements.txt`):
  - `requests>=2.31.0`
  - `beautifulsoup4>=4.12.0`
  - `lxml>=4.9.0`

## Installation

Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode (Recommended)

Launch the graphical interface:
```bash
python3 scraper_gui.py
```

**GUI Features:**
- Easy URL configuration with default parking/garage URL
- Adjustable scraping parameters (max pages, target records)
- Optional detailed information extraction
- Real-time progress tracking with page counter
- Activity log with timestamps
- Custom output directory and filename settings
- Start/stop controls with threading support

### Command Line Mode

Run the original command-line scraper:
```bash
python3 main.py
```

## Configuration Options

### GUI Configuration
- **OLX URL**: Target URL for scraping (defaults to Warsaw parking/garage rentals)
- **Max Pages**: Maximum number of pages to scrape (default: 20)
- **Target Records**: Maximum number of listings to collect (default: 300)
- **Detailed Scraping**: Get comprehensive information for each listing
- **Max Detailed**: Limit for detailed information extraction (default: 50)
- **Output Directory**: Where to save JSON files
- **Filename Prefix**: Custom prefix for output files

### Default URL
The scraper is pre-configured for Warsaw parking/garage rentals:
```
https://www.olx.pl/nieruchomosci/garaze-parkingi/wynajem/warszawa/?search%5Bphotos%5D=1&search%5Border%5D=created_at:desc
```

## Data Structure

### Basic Listing Data
```json
{
  "id": "listing_id",
  "title": "Parking spot title",
  "price": "Price in PLN",
  "location": "Location details",
  "date": "Posting date",
  "url": "Full listing URL",
  "image_url": "Main image URL"
}
```

### Detailed Listing Data
Includes all basic fields plus:
```json
{
  "detailed_title": "Full title from detail page",
  "detailed_price": "Detailed price information",
  "description": "Full listing description",
  "detailed_location": "Complete location details",
  "seller_name": "Seller name",
  "seller_type": "Individual/Business",
  "phone_number": "Contact number (if available)",
  "images": ["array", "of", "image", "urls"],
  "attributes": {"key": "value", "pairs": "of", "listing": "attributes"},
  "posted_date": "When listing was posted",
  "viewed_count": "Number of views",
  "safety_tips": ["array", "of", "safety", "tips"],
  "listing_features": ["special", "features", "or", "highlights"]
}
```

## Output Files

The scraper generates timestamped JSON files:
- `parking_listings_basic_YYYYMMDD_HHMMSS.json` - Basic listing information
- `parking_listings_detailed_YYYYMMDD_HHMMSS.json` - Detailed information (if enabled)

## Rate Limiting & Ethics

The scraper includes built-in delays to be respectful to OLX servers:
- 2-second delay between pages for basic scraping
- 3-second delay between detailed listings
- Configurable timeouts and error handling

**Please use responsibly:**
- Don't scrape excessively
- Respect OLX's terms of service
- Consider the server load
- Use data ethically and legally
- Avoid automated bulk downloads
- Do not share scraped data publicly without permission
- Ensure compliance with local laws and regulations
- Use the scraper for personal or research purposes only
- Avoid commercial use without explicit consent from OLX
- Report any issues or changes in OLX's structure to the repository maintainers

## Troubleshooting

### Common Issues

1. **No listings found**:
   - Check if the URL is correct and accessible
   - OLX may have changed their page structure
   - Try with a different URL or location

2. **Connection errors**:
   - Check your internet connection
   - OLX might be blocking requests (try again later)
   - Use a VPN if needed

3. **Empty results**:
   - The page structure might have changed
   - Check the debug HTML file generated for inspection
   - May need to update CSS selectors

### Debug Mode

The scraper saves debug HTML files (`debug_page.html`) for the first page scraped, which helps in troubleshooting selector issues.

### Error Handling

- Graceful handling of network timeouts
- Skip invalid listings without stopping
- Detailed error logging in GUI mode
- Automatic retry mechanisms for temporary failures

## Project Structure

```
PSpots-scraper/
├── main.py                 # Original CLI scraper
├── scraper_gui.py         # GUI application
├── launcher.py            # Interface launcher
├── run_scraper.sh         # Shell script launcher
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── output/               # Generated JSON files (created automatically)
```

## Technical Details

### Architecture
- **OLXScraper**: Core scraping class with robust selectors
- **OLXScraperGUI**: Tkinter-based graphical interface
- **OLXScraperWithProgress**: Extended scraper with progress callbacks
- **Threading**: Non-blocking UI during scraping operations

### Web Scraping Approach
- Multiple CSS selector fallbacks for reliability
- BeautifulSoup for HTML parsing
- Session-based requests with proper headers
- User-Agent rotation to appear more natural

### Data Extraction
- Smart text extraction with multiple selector attempts
- URL cleaning and ID extraction
- Image URL collection and deduplication
- Attribute parsing from various page sections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with OLX.pl's terms of service and applicable laws when using this scraper.

## Disclaimer

This tool is provided as-is for educational purposes. Users are responsible for ensuring their use complies with OLX.pl's terms of service and applicable laws. The authors are not responsible for any misuse of this software.