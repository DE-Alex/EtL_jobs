from bs4 import BeautifulSoup

def Soup(PageSource):
	soup = BeautifulSoup(PageSource,'html.parser')
	print 'Soup done!'
		
	#Get list of tags <script> with type="text/javascript". Usually 10-20 found.
	find_Tag = soup.findAll('script', type="text/javascript")
	
	#TODO templates to parse HTML pages
	
	#in tag list find tag with text 'jobs','title' and 'description' and get it.Usually 1 found.
	find_json = []
	for i in find_Tag:
		if i.string != None: 
			if 'jobs' and 'title' and 'description' in i.string:
				find_json.append(i.string)
				
	
	#Cut off all before "jobs":
	L = find_json[0].split('"jobs":')
	L = L[1] 
				
	#Cut off all after "jobs":[...]
	Job_str = ''
	k = 0
	for i in L:
		Job_str = Job_str + i
		if i == u'[': k += 1
		elif i == u']':	k -= 1
			
		if k == 0: 
			break

	return Job_str
	


if __name__ == '__main__':
	from bs4 import BeautifulSoup
	import csv 
	import codecs #to read/write unicode files in Python 2.6
	
	filename = 'J:\\Google\\Python\\PY\\Parser\\DataToScrape\\Freelance Python Jobs Online - Upwork.html'
	
	#!!!!!!!!
	#ReadFile = codecs.open(filename, encoding = 'UTF-8')
	ReadFile = codecs.open(filename, encoding = 'cp866')
	#!!!!!!!!
	PageSource = ReadFile.read()
	ReadFile.close()
	
	Job_str = Soup(PageSource)
	
	#converting string Job_str (format JSON) to Python objects
	import json
	Jobs_obj = json.loads(Job_str, encoding = 'utf-8')
	print 'Jobs list (JSON) to PyObj - Ok'
	
	csvFile = open('J:\\Google\\Python\\PY\\Parser\\data\\data.csv', 'ab')
	for job in Jobs_obj:
		print job
		csv_row = [v for k,v in job.items()]
		writer = csv.writer(csvFile, delimiter = ';')
		writer.writerow(csv_row)
		
	csvFile.close()
	print 'Add OK'
	

	