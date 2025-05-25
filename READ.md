# Facebook Group Scraper (Selenium)

A minimal Python script to extract visible posts from a Facebook group using your browser session cookies.

## Features
- Simulates login using exported Facebook cookies
- Scrolls automatically to load more content
- Clicks all "See more" buttons to expand full posts
- Deduplicates and exports posts to `facebook_group_posts.csv`

## Requirements
- Python 3.10+
- Google Chrome
- Matching `chromedriver`

## Usage

1. Run `facebook_login_capture.py` to export your cookies to `facebook_cookies.json`
2. Run `fb_scraper_cookie_method.py` to start scraping the group posts

## Notes
- This project is for **educational purposes only**.
- Do not scrape groups you are not a part of.
- `facebook_cookies.json` is private — **do not upload it**.
