# -*- coding: utf-8 -*-
import re
import scrapy


class JamaicaSpider(scrapy.Spider):
    name = 'jamaica'
    base_url = 'https://www.findyello.com/Jamaica/{}/'
    category_url = []
    popular_categories = []
    categories = []
    # start_urls = ['https://www.findyello.com/search/category-search']
    
    countries = ['Anguilla', 'Aruba', 'Barbados', 'Belize', 'Bonaire', 'British-Virgin-Islands', 'Cayman-Islands',
    'Dominica', 'Grenada', 'Guyana', 'Jamaica', 'Montserrat', 'St-Kitts', 'St-Lucia', 'St-Vincent', 'Turks-Caicos', 'Trinidad']

    def start_requests(self):
        urls = [
            'https://www.findyello.com/Jamaica/',
            'https://www.findyello.com/search/category-search',
        ]
        for url in urls:
        	if url is 'https://www.findyello.com/Jamaica/':
        		yield scrapy.Request(url=url, callback=self.parse_popular, errback=lambda x, url=url: self.errback_url_logger(x, url))
        	else:
        		yield scrapy.Request(url=url, callback=self.parse, errback=lambda x, url=url: self.errback_url_logger(x, url))
    
    def closed(self, reason):
    	with open('jamaicayp.csv','r') as in_file, open('websites.csv','w') as out_file:
		    seen = set() # set for fast O(1) amortized lookup
		    website = set()
		    website.add('')
		    for line in in_file:
		    	line = line.replace('http://http://', 'http://')

		        if line in seen: continue # skip duplicate

		        url = line.split(',')[0]
		        
		        if url in website: continue # skip duplicate website

		        seen.add(line)
		        website.add(url)
		        out_file.write(line)

    def errback_url_logger(self, e, url):
    	self.logger.error(url)

    def formatter(self, lst):
    	lst = list(map(lambda x: x.replace('& ', ''), lst))
    	lst = list(map(lambda x: x.replace(' ', '-'), lst))
    	lst = list(map(lambda x: x.replace(',', ''), lst))
    	lst = list(map(lambda x: x.replace('"', ''), lst))
    	lst = list(map(lambda x: x.replace('/jamaica/', '') if '/jamaica/' in x else x, lst))
    	lst = list(set(lst))
    	return lst

    def parse(self, response):
    	item = {'categories': response.css('a::attr(data-search-name)').extract()}
    	items = self.formatter(item['categories'])
    	self.categories = items
    	
    	for i in items:
    		if i in self.countries or i in self.popular_categories: continue
    		if i == 'Fireworks': i = 'Fire-works'

    		self.category_url = self.base_url.format(i) + '{}'
    		url = self.category_url.format('0')
    		yield scrapy.Request(url=url, callback=self.parse_data, errback=lambda x, url=url: self.errback_url_logger(x, url))

    def parse_popular(self, response):
    	item = {'categories': response.css('div.popular-searches').css('a.button.search-term::attr(href)').extract()}
    	items = self.formatter(item['categories'])
    	self.popular_categories = items
    	
    	for i in items:
    		if i in self.countries or i in self.categories: continue
    		self.category_url = self.base_url.format(i) + '{}'
    		url = self.category_url.format('0')
    		yield scrapy.Request(url=url, callback=self.parse_data, errback=lambda x, url=url: self.errback_url_logger(x, url))
    
    def parse_data(self, response):
    	if response.css('article'):
	    	try:
	    		number_listing = len(response.css('section#listings article'))

	    		for i in range(number_listing):
		        	listing = response.css('#bus-listing-{}'.format(i))

		        	try:
		        		email = listing.css('div.card-more-info.stacked-section').css('a[href*=mailto]::attr(href)')[0].extract().replace('mailto:', '')
		        	except Exception as e:
		        		email = ''

		        	try:
		        		website = listing.css('div.card-more-info.stacked-section').css('a[href*=www]::attr(href)')[0].extract()
		        	except Exception as e:
		        		website = ''

		        	try:
		        		phone = listing.css('a.open-phone-overlay::text')[1].extract().strip('\n').strip('\t')
		        	except Exception as e:
		        		try:
		        			phone = listing.css('div.card-information.stacked-section').css('a::text')[1].extract().strip('\n').strip('\t')
		        		except Exception as e:
		        			try:
		        				phone = listing.css('div.card-phone').css('a').xpath('span/text()')[0].extract()
		        			except Exception as e:
		        				phone = ''

		        	try:
		        		address = listing.css('div.stacked-section.address span::text')[1].extract()
		        	except Exception as e:
		        		try:
		        			address = listing.css('div.stacked-section.address span::text')[0].extract()
		        		except Exception as e:
		        			address = ''

		        	if phone is '' and email is '' and website is '' and address is '': continue

			        item = {
			        	'company_name': listing.css('div.listing-title').xpath('a/text()').extract_first(),
			        	'address': address,
			        	'phone': phone,
			        	'email': email,
			        	'website': website,
			        	'category': response.url.split('/')[4]
			        }

		        	yield item
	    	except Exception as e:
	    		self.logger.error('{} -> {}'.format(e, response.url))

	    	page = int(response.url.split('/')[5]) + 1
	    	next_page_url = self.category_url.format(page)
	    	yield scrapy.Request(url=next_page_url, callback=self.parse_data)
