Filters = {'Category': {'Any Category': '',
						'******': 'c/' + '*******'
						},
						
		'Sub Cat': {'Any Sub Category': '',
						'******': 'sc/' + '*******'
						},

			'Job Type': {'Any Job Type': '',
						'Hourly': 't/0/',
						'Fixed Price': 't/1/'
						},
						
			#For Fixed Price only
			'Budget': {'Any Budget': '',
						'Less than $100': 'amount=0-99',
						'$100-$500': 'amount=100-499',
						'$500-$1k': 'amount=500-999',
						'$1k-$5k': 'amount=1000-4999',
						'$5K+': 'amount=5000-',
						'$Min $Max': 'amount=Min-Max'
						},				
						
	'Client History': {'Any Client History': '',
						'No Hires': 'client_hires=0',
						'1 to 9 Hires': 'client_hires=1-9',
						'10+ Hires': 'client_hires=10-'
						},
						
	'Experience Level': {'Any Experience Level': '',
						'Entry Level': 'contractor_tier=1',
						'Intermediate': 'contractor_tier=2',
						'Expert': 'contractor_tier=3'
						},
						
	#For Hourly Job Type only
	'Project Length': {'Any Project Length': '',
						'Less than 1 week': 'duration=days',
						'Less than 1 month': 'duration=weeks',
						'1 to 3 months': 'duration=months',
						'More than 3 months': 'duration=ongoing'
						},
						#Combination:duration=days,weeks,months,ongoing
						
		'Client Location': {'Any location': ''
						},
						
		'Client Info': {'Any Client': '',
						'My Previous Clients': 'previous_client=all',
						'Payment Verified': 'payment_verified=1'
						},
						#Combination: previous_client=all&payment_verified=1

'Number of Proposals': {'Any Number of Proposals': '',
						'Less than 5': 'proposals=0-4',
						'5 to 10': 'proposals=5-9',
						'10 to 15': 'proposals=10-14',
						'15 to 20': 'proposals=15-19',
						'20 to 50': 'proposals=20-49'
						},
					
	#For Hourly Job Type only
	'Hours per Week': {'Any Hours per Week': '',
						'Less than 30 hrs/week': 'workload=as_needed',
						'More than 30 hrs/week': 'workload=full_time'
						},
					
	#Category
	#...
	#Client location
	#...
}

default_selection = {'Category':'',
					'Sub Cat':'',
					'Job Type':'',
					'Budget':'',
					'Client History':'',
					'Experience Level':'',
					'Project Length':'',
					'Client Location':'',
					'Client Info':'',
					'Number of Proposals':'',
					'Hours per Week':''
					}

def RequestGeneration(wordslist, selection):
	
	Request = ''
	
	base_request = ['https://www.upwork.com/o/jobs/browse/',
					'Category',
					'Sub Cat',
					'Job Type',
					'?',
					'Budget',
					'Client History',
					'Experience Level',
					'Project Length',
					'Client Location',
					'Client Info',
					'Number of Proposals',
					'q=' + '%20'.join(wordslist), #q=Data%20and%20mining%20and%20python
					'sort=renew_time_int%2Bdesc',
					'Hours per Week'
					]
	
		
	for item in base_request:
		for filter in Filters:
			if filter in item:
				item = item.replace(filter,selection[filter])
			else:
				pass
		
		if len(Request) == 0:
			Request = Request + item
		elif (Request[-1] == '/') or (Request[-1] == '?'):
			Request = Request + item
		elif item == '':
			Request = Request + item
		else:
			Request = Request + '&' + item
	
	return Request

	
if __name__ == '__main__':
	wordslist = ['Word1']
	#wordslist = ['Word1','Word2','Word3']
	selection = default_selection
	Request = RequestGeneration(wordslist, selection)
	print Request

