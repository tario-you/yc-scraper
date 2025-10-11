# Y Combinator Directory Scraper

Live explorer: [yc-scraper-five.vercel.app](https://yc-scraper-five.vercel.app/) · Maintained by [Tario You](https://linkedin.com/in/tario-you)

I built YC-Scraper to create a dataset of all the companies in the [Y Combinator directory](https://www.ycombinator.com/companies/). You can search for companies by industry, region, company size, and more in this directory.

This fork also includes a plain HTML/CSS/JS explorer—no build tools or frameworks required.

## About Y Combinator

Y Combinator is a startup accelerator that has invested in over 4,000 companies that have a combined valuation of over $600B. The overall goal of Y Combinator is to help startups really take off.

## Requirements

You must have [Firefox](https://www.mozilla.org/en-US/firefox/new/) and [geckodriver](https://github.com/mozilla/geckodriver/releases) installed. You can install `geckodriver` by running `brew install geckodriver`.

Python packages include:

- [Scrapy](https://scrapy.org)
- [Selenium](https://www.selenium.dev/documentation/)
- [tqdm](https://tqdm.github.io)
- [Pandas](https://pandas.pydata.org) (optional)

## Usage

1. Clone this repository.
2. Move to the `yc-scraper` directory. (Optional) Create a virtual environment and install the dependencies with `pip install -r requirements.txt`.
3. Export the Algolia credentials exposed by the YC directory (visible in the browser network panel) and run the parallel link extractor:

    ```bash
    export ALGOLIA_APP_ID="45BWZJ1SGC"
    export ALGOLIA_API_KEY="<your-search-only-key>"
    # optional override; defaults to YCCompany_production
    export ALGOLIA_INDEX="YCCompany_production"
    python scripts/yc_links_extractor.py
    ```

    This writes `scrapy-project/ycombinator/start_urls.txt` for the spider.
4. Run `scrapy runspider scrapy-project/ycombinator/spiders/yscraper.py -o output.jl`. The resulting JSON Lines file can be read directly in Pandas:

    ```python
    import pandas as pd
    df = pd.read_json('output.jl', lines=True)
    ```

5. (Optional) Turn the crawl output into a UI-ready JSON bundle and launch the static explorer:

    ```bash
    python scripts/convert_output_to_json.py
    python -m http.server 3000  # open http://localhost:3000
    ```

## Dataset

Check out the dataset I published on [Kaggle.com](https://www.kaggle.com/datasets/miguelcorraljr/y-combinator-directory).

## Attributes

|  Attribute           |  Description | Data Type  |
|-----------------------|---|---|
| company_id            | Company id provided by YC  | int  |
| company_name          | Company name  | string  |
| short_description     | One-line description of the company  | string  |
| long_description      | Long description of the company  | string  |
| batch                 | Batch name provided by YC  | string  |
| status                | Company status  | string  |
| tags                  | Industry tags  | list  |
| location              | Company location | string  |
| country               | Company country  | string  |
| year_founded          | Year the company was founded  | int  |
| num_founders          | Number of founders  | int  |
| founders_names        | Full names of the founders  | list  |
| founder_details       | Extended founder bios and social links | list  |
| team_size             | Number of employees  | int  |
| website               | Company website   | string  |
| cb_url                | Company Crunchbase url  | string  |
| linkedin_url          | Company LinkedIn url  | string  |

## Sample Data

Note: I excluded 'short_description', 'long_description', 'cb_url', and 'linkedin_url'  in the sample data for brevity.

| company_id | company_name | short_description                         | batch | status   | tags                                                      | location      | country | year_founded | num_founders | founders_names                                       | team_size | website                  |   |
|------------|--------------|-------------------------------------------|-------|----------|-----------------------------------------------------------|---------------|---------|--------------|--------------|------------------------------------------------------|-----------|--------------------------|---|
| 240        | Stripe       | Economic infrastructure for the internet. | S09   | Active   | ['Fintech', 'Banking as a Service', 'SaaS']               | San Francisco | US      |              | 2            | ['John Collison', 'Patrick Collison']                | 7000      | <http://stripe.com>        |   |
| 271        | Airbnb       | Book accommodations around the world.     | W09   | Public   | ['Travel', 'Marketplace']                                 | San Francisco | US      | 2008         | 3            | ['Nathan Blecharczyk', 'Brian Chesky', 'Joe Gebbia'] | 6132      | <http://airbnb.com>        |   |
| 325        | Dropbox      | Backup and share files in the cloud.      | S07   | Public   | []                                                        | San Francisco | US      | 2008         | 2            | ['Arash Ferdowsi', 'Drew Houston']                   | 4000      | <http://dropbox.com>       |   |
| 379        | Reddit       | The frontpage of the internet.            | S05   | Acquired | ['Community', 'Social', 'Social Media', 'Social Network'] | San Francisco | US      |              | 1            | ['Steve Huffman']                                    | 201       | <http://reddit.com>        |   |
| 439        | Coinbase     | Buy, sell, and manage cryptocurrencies.   | S12   | Public   | ['Crypto / Web3']                                         | San Francisco | US      | 2012         | 1            | ['Brian Armstrong']                                  | 6112      | <https://www.coinbase.com> |   |
| 531        | DoorDash     | Restaurant delivery.                      | S13   | Public   | ['E-commerce', 'Marketplace']                             | San Francisco | US      | 2013         | 3            | ['Andy Fang', 'Stanley Tang', 'Tony Xu']             | 8600      | <http://doordash.com>      |   |

## Meta

Author: Miguel Corral Jr.  
Email: <corraljrmiguel@gmail.com>  
LinkedIn: <https://www.linkedin.com/in/imiguel>  
GitHub: <https://github.com/corralm>

Distributed under the MIT license. See [LICENSE](./LICENSE) for more information.
