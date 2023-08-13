import os, time

def RequestGen(link, login, password, Template_path, KeyList_Words, Requests_file):
	if Template_path != False: 
		#*************import importlib***********************
		from MyLibs.Dinamic_import_module_by_path import Import_by_path
		template = Import_by_path(Template_path)
		#**************************************
		print("Template found. Generating request...")
		selection = template.default_selection #TODO Selection!
		for wordslist in KeyList_Words:
			Request = template.RequestGeneration(wordslist, selection)
			print('wordslist:', wordslist)
			Requests_file.write(link +'\t'+ ','.join(wordslist) +'\t'+ Request +'\n')
	else:
		print("Template in not found. Try to load by link")
		Request = link

		for wordslist in KeyList_Words:
			Requests_file.write(link +'\t'+ ','.join(wordslist) +'\t'+ Request + '\n')
		
	Answer = 'Requests saved to file\n'	
	return Answer

	
if __name__ == '__main__':
		
	import MyLibs.PC_or_Mobile 
	CWD = MyLibs.PC_or_Mobile.Check_for_CWD() #checking work directory
	print(CWD)
	
	
	site = 'www_Upwork_com'
	link = 'https://www.upwork.com/o/jobs/browse/'
	login, password = 'xxxx', 'xxxx'
	Template_path = '\\data\\Templates' + '\\' + site
	KeyList_Words = [['python'], ['parsing']]
	
	Requests_file = open(CWD + '\\Requests.txt', 'w')
	Answer = RequestGen(link, login, password, Template_path, KeyList_Words, Requests_file)
	print(Answer)
	Requests_file.close()
	
