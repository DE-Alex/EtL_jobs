import os, time, requests
#!!!!!!!!!!!!!!!!!
import importlib
#!!!!!!!!!!!!!!!!!

def Scan(CWD, Folders_List):
	print '\n','.'*20,'Data from folders','.'*20,'\n'
	print 'Reading sites, logins, passwords, templates ...\n'

	Templates_scan = {}
	
	for site in Folders_List:
		folder = Folders_List[site]
		try:
			password_file = open(CWD + '\\Templates\\' + folder + '\\Password.txt')
			read_password = password_file.read().rstrip()	#read and kill \n symbol 
			if len(read_password.split()) == 2:
				Login, Password = read_password.split()
			else:
				print '! Error in %s: %s' %(folder, read_password.split())
				Login, Password = 'Error!', 'Error!'
		except IOError:
			Login, Password = None, None
						
		template_path = '\\Templates\\' + folder + '\\Template.py'
				
		if os.path.exists(CWD + template_path) == False: 
			template_path = None
				
		Templates_scan[folder] = Login, Password, template_path
		
		print 'Site:', folder, ', Login: %s, Password: %s, Template: %s' %(Templates_scan[folder])
	
	
	return Templates_scan

def RequestFunc(folder, link, Templates_scan_folder, KeyList_Words, Requests_file):
	if Templates_scan_folder != None: 
		Login, Password, template_path = Templates_scan_folder
	else: 
		Login, Password, template_path = None, None, None
		
	if template_path != None: 
		print  "Template found. Try to load by link..."
		#************************************
		module_path = template_path[1:-3].replace('\\','.')
		print module_path
		template = importlib.import_module(module_path)#AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA!!!!!!!!!!!!!!!!!!
		#**************************************
		print 'Import done!!!'
		selection = template.default_selection #TODO Selection!
		for wordslist in KeyList_Words:
			Request = template.RequestGeneration(wordslist, selection)
			print 'wordslist:', wordslist
			Requests_file.write(link +'\t'+ ','.join(wordslist) +'\t'+ Request +'\t'+ Login +'\t'+ Password + '\n')
	else:
		print "Template in not found. Try to load by link"
		Request = link
		if Login == None: Login = 'None'
		if Password == None: Password = 'None'
		Requests_file.write(link +'\t'+ 'KeyList_Words -unknown-' +'\t'+ Request +'\t'+ Login +'\t'+ Password + '\n')
		
	Answer = 'Requests saved to file\n'	
	return Answer

	

	
if __name__ == '__main__':
	import os, sys
	import Templates.Folders_List
	
	if sys.path[0] == '\\storage\\emulated\\0\\qpython':
		CWD = sys.path[0] + '\\projects\\parser'
	else:
		CWD = sys.path[0]	
		
	Folders_List = Templates.Folders_List.List
	Scan(CWD, Folders_List)
	
	'''
	Templates_scan  = Scan(CWD, Folders_List)
	print 'Ok!', Folders_List
	'''
	
	
	folder = 'www_upwork_com'
	link = 'https://www.upwork.com/o/jobs/browse/'
	Templates_scan_folder = 'Login', 'Password', ('\\Templates\\' + folder + '\\Template.py')
	KeyList_Words = [['python'], ['parsing']]
	Requests_file = open(CWD + '\\Requests.txt', 'w')
	
	print RequestFunc(folder, link, Templates_scan_folder, KeyList_Words, Requests_file)
	
