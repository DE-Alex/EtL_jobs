import os, sys, shutil
	
#checking for desktop or mobile
#because of different work directory when start on PC or Mobile
def Check_for_CWD():
	if sys.path[0] == '\\storage\\emulated\\0\\qpython':
		CWD = sys.path[0] + '\\projects\\parser'
	else:
		CWD = sys.path[0]
	return CWD
		
def Check_for_ComputerName():
	if ('ComputerName' in os.environ) and (os.environ['ComputerName'] == 'OPR-5'): flag = 'Local'
	else: flag = 'OnLine'
	print 'FLAG =',flag 
	return flag	
	
	
#checking files for BIG_FILE_NAMES wich appear after editing them with smartfone
#renaming if BIG_FILE_NAMES found
def Check_for_BIGNAMES(CWD):
	for root, dirs, files in os.walk(CWD):
		#print root, ':'
		for file in files:
			if file.isupper() == True:
				print 'Rename:', file, 'to', file.capitalize()
				FILE_NAME = root + '\\' + file
				file_name = root + '\\' + file.capitalize()
				shutil.move(FILE_NAME, file_name)
			#else: print '- Ok'
				

		
if __name__ == '__main__':
	CWD = Check_for_CWD()
	print 'CWD=',CWD
	
	flag = Check_for_ComputerName()

	Check_for_BIGNAMES(CWD)