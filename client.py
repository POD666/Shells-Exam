from pysimplesoap.client import SoapClient, SoapFault

client = SoapClient(
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/', # SOAPAction
    namespace = "http://example.com/sample.wsdl", 
    soap_ns='soap',
    trace = False,
    ns = False)

# call the remote method
#response = client.LOGIN(address='192.168.1.108', user='root', password='root')

print "Client shell"
while 1:
	cmd = raw_input(">").split(' ')
	if cmd[0].upper() == 'LOGIN':
		response = client.LOGIN(address=cmd[1], user=cmd[2], password=cmd[3])
	elif cmd[0].upper() == 'LOGOUT':
		response = client.LOGOUT()

	elif cmd[0].upper() == 'BIDIR':
		response = client.BIDIR(a=cmd[1], b=cmd[2])
	elif cmd[0].upper() == 'UNIDIR':
		response = client.UNIDIR(src=cmd[1], dst=cmd[2])

	elif cmd[0].upper() == 'SET':
		response = client.SET(port=cmd[1], attr=cmd[2], value=cmd[3])
	elif cmd[0].upper() == 'GET':
		response = client.GET(port=cmd[1], attr=cmd[2])

	print response.Success, response.ResponseInfo
