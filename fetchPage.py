import socket
import config
import datetime
import threading

socket.setdefaulttimeout(config.timeout)

DNSCache = {}


class Error404(Exception):
    '''Can not find the page.'''
    pass

class ErrorOther(Exception):
    '''Some other exception'''
    def __init__(self,code):
        #print 'Code :',code
        pass
class ErrorTryTooManyTimes(Exception):
    '''try too many times'''
    pass

def downPage(hostname ,filename , trytimes=0):
    try :
        #To avoid too many tries .Try times can not be more than max_try_times
        if trytimes >= config.max_try_times : 
            raise ErrorTryTooManyTimes
    except ErrorTryTooManyTimes :
        return config.RESULTTRYTOOMANY,hostname+filename,None
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        #DNS cache
        if DNSCache.has_key(hostname):
            addr = DNSCache[hostname]
        else:
            addr = socket.gethostbyname(hostname)
            DNSCache[hostname] = addr
        #connect to http server ,default port 80
        s.connect((addr,80))
        msg  = 'GET '+filename+' HTTP/1.0\r\n'
        msg += 'Host: '+hostname+'\r\n'
        msg += 'User-Agent:%s\r\n\r\n' % (config.CRAWLER_NAME,)
        code = '' 
        f = None
        s.sendall(msg)
        first = True
        pageBuffer = ''
        while True:
            msg = s.recv(102400)
            if not len(msg):
                if f!=None:
                    f.flush()
                    f.close()
                break
            # Head information must be in the first recv buffer
            if first:
                first = False                
                headpos = msg.index("\r\n\r\n")
                code,other = dealwithHead(msg[:headpos])
                if code=='200':
                    #config.fetched_url += 1
                    f = open(config.DOWNLOAD_STORAGE_FOLDER + hostname + '-' + str(abs(hash(hostname+filename))),'w')
                    f.writelines(msg[headpos+4:])
                    pageBuffer += msg[headpos+4:]
                elif code=='301' or code=='302':
                    #if code is 301 or 302 , try down again using redirect location
                    if other.startswith("http") :                
                        hname, fname = parse(other)
                        downPage(hname,fname,trytimes+1)#try again
                    else :
                        downPage(hostname,other,trytimes+1)
                elif code=='404':
                    raise Error404
                else : 
                    raise ErrorOther(code)
            else:
                if f!=None :
                    f.writelines(msg)
                    pageBuffer += msg
        #s.shutdown(socket.SHUT_RDWR)
        s.close()
        return config.RESULTFETCHED,hostname+filename,pageBuffer
    except Error404 :
        return config.RESULTCANNOTFIND,hostname+filename,None
    except ErrorOther:
        return config.RESULTOTHER,hostname+filename,None
    except socket.timeout:
        return config.RESULTTIMEOUT,hostname+filename,None
    except Exception, e:
        return config.RESULTOTHER,hostname+filename,None
    

def dealwithHead(head):
    '''deal with HTTP HEAD'''
    lines = head.splitlines()
    fstline = lines[0]
    code =fstline.split()[1]
    if code == '404' : return (code,None)
    if code == '200' : return (code,None)
    if code == '301' or code == '302' : 
        for line in lines[1:]:
            p = line.index(':')
            key = line[:p]
            if key=='Location' :
                return (code,line[p+2:])
    return (code,None)
    
def parse(url):
    '''Parse a url to hostname+filename'''
    try:
        u = url.strip().strip('\n').strip('\r').strip('\t')
        if u.startswith('http://') :
            u = u[7:]
        elif u.startswith('https://'):
            u = u[8:]
        if u.find(':80')>0 :
            p = u.index(':80')
            p2 = p + 3
        else:
            if u.find('/')>0:
                p = u.index('/') 
                p2 = p
            else:
                p = len(u)
                p2 = -1
        hostname = u[:p]
        if p2>0 :
            filename = u[p2:]
        else : filename = '/'
        return hostname, filename
    except Exception ,e:
        print "Parse wrong : " , url
        print e

from BeautifulSoup import BeautifulSoup

def parsePage(pagebuf, url) :
    soup = BeautifulSoup(pagebuf) 
    hostname,filename = parse(url)
    alist = soup.findAll('a')
    hreflist = []
    for a_tag in alist :
        href = a_tag.get('href',None)
        if href != None :
            if href.startswith('/') :
                href = 'http://' + hostname + href
            hreflist.append(href)
    return hreflist
    

def PrintDNSCache():
    '''print DNS dict'''
    n = 1
    for hostname in DNSCache.keys():
        print n,'\t',hostname, '\t',DNSCache[hostname]
        n+=1

def dealwithResult(res,url):
    '''Deal with the result of downPage'''
    config.total_url+=1
    if res==config.RESULTFETCHED :
        config.fetched_url+=1
        print config.total_url , '\t fetched :', url
    if res==config.RESULTCANNOTFIND :
        config.failed_url+=1
        print "Error 404 at : ", url
    if res==config.RESULTOTHER :
        config.other_url +=1
        print "Error Undefined at : ", url
    if res==config.RESULTTIMEOUT :
        config.timeout_url +=1
        print "Timeout ",url
    if res==config.RESULTTRYTOOMANY:
        config.trytoomany_url+=1
        print e ,"Try too many times at", url

if __name__=='__main__':    
    print  'Get Page using GET method'
    
