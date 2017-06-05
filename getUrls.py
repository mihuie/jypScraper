with open('jamaicayp.csv','r') as in_file, open('websites.csv','w') as out_file:
    seen = set() # set for fast O(1) amortized lookup
    website = set()
    website.add('')
    for line in in_file:
    	line = line.replace('http://http://', 'http://')

        if line in seen: continue # skip duplicate

        url = line.split(',')[0]
        
        if url in website: continue # skip duplicate website

        # print url
        seen.add(line)
        website.add(url)
        out_file.write(line)
