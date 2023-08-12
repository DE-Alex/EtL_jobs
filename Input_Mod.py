def InputKeys(CWD):
	#Import Links and Keywords to parse  from Input_key.txt to KeyList
	print '.'*20,'Input Data','.'*20,'\n'
	print 'Reading from "Input_key.txt"...\n'
	Input_file = open(CWD + '\\Input_key.txt')
	

	Sorter = []
	Title = ['','Links:','Words:']
	
	for line in Input_file:
		line = line.rstrip()  #kill \n symbol 
		if line in Title: 
			checkline = Title.index(line) #checkline = 0...2 
			while len(Sorter) < checkline + 1: Sorter.append([]) #extending Sorter limits
		else:	
			Words = line.split()
			Sorter[checkline].append(Words) #appending lines that not in Title's list
		
	Links = []
	
	for link in Sorter[1]: Links.append(link[0]) #transform list[][] to list []
	Words = Sorter[2]
	
	KeyList = {'Links' : Links, 'Words' : Words}
	Input_file.close()
	
	return KeyList
	
	
if __name__ == '__main__':
	import sys
	import PC_or_Mobile
	CWD = PC_or_Mobile.Check_for_CWD()
	
	KeyList = InputKeys(CWD)
	print KeyList
	


