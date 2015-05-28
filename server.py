# pip install pysimplesoap
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
from datetime import datetime
# pip install ping
from ping import quiet_ping

logged_in_time = datetime(1990, 1, 1) ### server state 'logged out'

#decorator that checks if server is logged in.
def authorized(fn):
    def wrapped(*args, **kwargs):
        dif = datetime.now() - logged_in_time
        if dif.total_seconds()/60 >= 10:
            # not authorized so get error 
            return {'Success': 0, 'ErrorCode': 0, 'Log': '', 'ResponseInfo':'not logged in'}

        return fn(*args, **kwargs)
    return wrapped

def login(address, user, password):
    # what do we need user and password for? shoud i write some db with users credentials?

    #ping 2 times with 60sec timeout
    lost = quiet_ping(address, count = 2, timeout=60)[0] # get % of lost 

    #if 1 ping was success then not 100% lost so if not 100% then success
    success = int(not (lost == 100)) 

    if success:
        #force to use global 'logged_in_time' instead of creation local
        global logged_in_time ### server state 'logged in'
        logged_in_time = datetime.now()

    return {'Success': success, 'ErrorCode': 0, 'Log': '', 'ResponseInfo':'logged in'}

@authorized
def logout():
    #force to use global 'logged_in_time' instead of creation local
    global logged_in_time
    logged_in_time = datetime(1990, 1, 1) ### server state 'logged out'
    return {'Success': 1, 'ErrorCode': 0, 'Log': '', 'ResponseInfo':'logged out'}


BIDIR = {}

@authorized
def bidir(a, b):
    #If a previous BIDIR command already included the two ports (regardless of the order in which they appear)
    if BIDIR.get(a, None) == b or BIDIR.get(b, None) == a:
        msg = 'CONNECTION EXISTS'
    
    #If at least one port appeared before but not in the same command with the other port (regardless in which
    #field it appeared in before)
    elif a in BIDIR.values() or b in BIDIR.values() or a in BIDIR.keys() or b in BIDIR.keys():
        msg = 'CONNECTION USED'

    #If none of the ports appeared before
    else:
        BIDIR[a] = b
        msg = 'CONNECTION CREATED'

    return {'Success': 1, 'ErrorCode': 0, 'Log': '', 'ResponseInfo':msg}

UNIDIR = {}

@authorized
def unidir(src, dst):
    #If a previous UNIDIR command already included the two ports (in the same order)
    if UNIDIR.get(src, None) == dst:
        msg = 'CONNECTION EXISTS'

    #If a previous UNIDIR command already included the two ports (in the opposite order)
    elif UNIDIR.get(dst, None) == src:
        UNIDIR[src] = dst
        msg = 'CONNECTION CREATED'

    #If the SrcPort appeared in a previous UNIDIR command with a different DstPort then the current one
    elif UNIDIR.get(src, None):
        UNIDIR[src] = dst
        msg = 'SrcPORT is USED - Creating additional connection'

    #If the DstPort appeared in a previous UNIDIR command with a different SrcPort then the current one
    elif dst in UNIDIR.values():
        msg = 'DstPORT is USED - Not creating an additional connection'

    #I think it shoud be
    else:
        UNIDIR[src] = dst
        msg = 'CONNECTION CREATED'

    return {'Success': 1, 'ErrorCode': 0, 'Log': '', 'ResponseInfo':msg}

ATTR = {}

@authorized
def set_attr(port, attr, value):
    ATTR[port+'@'+attr] = value
    return {'Success': 1, 'ErrorCode': 0, 'Log': '', 'ResponseInfo':''}

@authorized
def get_attr(port, attr):
    return {'Success': 1, 'ErrorCode': 0, 'Log': '', 'ResponseInfo': ATTR.get(port+'@'+attr, None)}


# copypast from tutorial
dispatcher = SoapDispatcher(
    'my_dispatcher',
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/', # SOAPAction
    namespace = "http://example.com/sample.wsdl", 
    prefix="ns0",
    trace = True,
    ns = True)


response_tamplate = {'Success': int, 'ErrorCode': int, 'Log': str, 'ResponseInfo':str}

dispatcher.register_function('LOGIN', login, returns=response_tamplate, args={'address':str, 'user': str, 'password': str})
dispatcher.register_function('LOGOUT', logout, returns=response_tamplate, args={})

dispatcher.register_function('BIDIR', bidir, returns=response_tamplate, args={'a':str, 'b':str})
dispatcher.register_function('UNIDIR', unidir, returns=response_tamplate, args={'src':str, 'dst':str})

dispatcher.register_function('SET', set_attr, returns=response_tamplate, args={'port':str, 'attr':str, 'value':str})
dispatcher.register_function('GET', get_attr, returns=response_tamplate, args={'port':str, 'attr':str})


print "Starting server..."
httpd = HTTPServer(("", 8008), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.serve_forever()