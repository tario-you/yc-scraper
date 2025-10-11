import json
from pathlib import Path

import scrapy


BASE_DIR = Path(__file__).resolve().parent.parent
START_URLS_PATH = BASE_DIR / "start_urls.txt"


def make_start_urls_list():
    """Returns a list with the start urls."""
    with START_URLS_PATH.open("r", encoding="utf-8") as f:
        return json.loads(f.read())


class YCombinator(scrapy.Spider):
    """Crawls ycombinator.com/companies and extracts data about each company."""
    name = 'YCombinatorScraper'
    start_urls = make_start_urls_list()

    def parse(self, response):
        rc = response.css
        # get the JSON object inside the <script> tag
        # cl = 'script.js-react-on-rails-component'
        # st = rc(f'{cl}[data-component-name="CompaniesShowPage"]::text').get()
        st = response.css('[data-page]::attr(data-page)').get()
        if not st:
            return
        # load the JSON object and set the variable for the 'Company' data
        jo = json.loads(st)['props']
        jc = jo['company']
        founders = jc['founders']
        yield {
            'company_id': jc['id'],
            'company_name': jc['name'],
            'short_description': jc['one_liner'],
            'long_description': jc['long_description'],
            'batch': jc['batch_name'],
            'status': jc['ycdc_status'],
            'tags': jc['tags'],
            'location': jc['location'],
            'country': jc['country'],
            'year_founded': jc['year_founded'],
            'num_founders': len(founders),
            'founders_names': [f['full_name'] for f in founders],
            'founder_details': [
                {
                    'name': f.get('full_name'),
                    'title': f.get('title'),
                    'bio': f.get('founder_bio'),
                    'linkedin_url': f.get('linkedin_url'),
                    'twitter_url': f.get('twitter_url'),
                }
                for f in founders
            ],
            'team_size': jc['team_size'],
            'website': jc['website'],
            'cb_url': jc['cb_url'],
            'linkedin_url': jc['linkedin_url'],
        }
