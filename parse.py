from bs4 import BeautifulSoup
import sys
if sys.path[0] == '\\storage\\emulated\\0\\qpython':
	CWD = sys.path[0] + '\\projects\\parser'
else:
	CWD = sys.path[0]


def Soup(file):
	#CWD = os.getcwd()
	#file = open(CWD + '\\Save\\' + 'upw.html')
	soup = BeautifulSoup(file,'html.parser')
	#print soup.prettify()
	return soup
	
	
	


	
'''
def Parse(filename, Site_list, CWD):
	for site in Site_list:
		path = CWD + '/Templates/'+ site
		if os.path.exists(path + '/template.dbm'):
			print 'Template for %s found:' %(site)
			#TODO: if found Default - use (D)efault template or create (N)ew or (U)pdate filters from site
			#TODO: if found list of templates - print list and choose one or (U)pdate filters from site
		elif os.path.exists(path + '/Filters.txt'):
			print 'Template not found, creating default.'
			#TODO: create default template from Filters
		else:
			print 'Template dnf Filters for %s not found. Create it before parse.'
			#TODO: exit?
		
	return filename
'''	


if __name__ == '__main__':

	if sys.path[0] == '\\storage\\emulated\\0\\qpython':
		CWD = sys.path[0] + '\\projects\\parser'
	else:
		CWD = sys.path[0]
	
	file = open(CWD + '\\Save\\' + 'upw.html')
	soup = Soup(file)
	file.close
	print 'soup ok'
	
	nice_file = soup.prettify()
	fileTo = open(CWD + '\\Save\\' + 'upw_prettify.html', 'w')
	fileTo.write(nice_file)
	print 'pretty file ok'
	
	