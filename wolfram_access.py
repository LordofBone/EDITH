import wolframalpha
#you can get your own API key here https://products.wolframalpha.com/simple-api/documentation/
client = wolframalpha.Client("YOUR KEY HERE")

def runQuery(query):
	res = client.query(query)
	
	try:
		(next(res.results).text)
	except:
		return("Invalid query or no results")
	
	return (next(res.results).text)

#if called direct then run the function
if __name__ == '__main__':
	qIn = input('Enter query:	')
	print(runQuery(qIn))