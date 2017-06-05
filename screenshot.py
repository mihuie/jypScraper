from pyvirtualdisplay import Display
from selenium import webdriver
import csv, re

url_pattern = re.compile("^((https?):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*$")
urls = []
seen = []


with open('websites.csv', 'rb') as csvfile:

    # get number of columns
    for line in csvfile.readlines():
        array = line.split(',')
        first_item = array[0]

    num_columns = len(array)
    csvfile.seek(0)

    reader = csv.reader(csvfile, delimiter=',')
    included_cols = [0]

    for row in reader:
        content = list(row[i] for i in included_cols)[0]
        if content != '' and re.match(url_pattern, content) and content not in seen:
            urls.append(content)
            seen.append(content)

    # print urls


display = Display(visible=0, size=(1366, 768))
display.start()

browser = webdriver.Firefox()
browser.set_window_size(1366, 768)

for url in urls:
	try:
		browser.get(url)
		# set timeouts
		browser.set_script_timeout(30)
		browser.set_page_load_timeout(30) # seconds

		browser.get_screenshot_as_file((browser.title).replace('.', '_') + '.png')
	except:
		print 'Timed out retrieving: ' + url

browser.quit()
display.stop()