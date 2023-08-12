	
def Clear(link):
	clear_link = link
	for letter in ['://','/','\\',':','*','?','"','>','<','|']:
		if letter in clear_link: clear_link = clear_link.replace(letter,'_')
	return clear_link
	


if __name__ == '__main__':
	
	link = 'https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending'
	print Clear(link)
	print 'Done'
	