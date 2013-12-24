import fetchPage
import threadpool
import datetime
import config
import urllib2

main = threadpool.ThreadPool(config.THREAD_COUNT)

PAGESCache = {}

def callbackfunc(request,result):
    res,resource,pagebuf = result
    if pagebuf == None :
        return
    
    hreflist = fetchPage.parsePage(pagebuf, resource)
    for href in hreflist :
        if PAGESCache.get(href,None) == None : PAGESCache[href] = True 
        else : continue
        hostname,filename = fetchPage.parse(href)
        main.putRequest(threadpool.WorkRequest(fetchPage.downPage,args=[hostname,filename],kwds={},callback=callbackfunc))
    fetchPage.dealwithResult(res,resource)
    

def usingThreadpool(limit,num_thread):
    urlset = open(config.SEED_FILE, "r")
    start = datetime.datetime.now()
    for url in urlset :
        try :
            if PAGESCache.get(url,None) == None : PAGESCache[url] = True 
            else : continue
            hostname , filename = fetchPage.parse(url)
            req = threadpool.WorkRequest(fetchPage.downPage,args=[hostname,filename],kwds={},callback=callbackfunc)
            main.putRequest(req)
        except Exception:
            pass
    while True:
        try:
            main.poll()
            if config.total_url >= limit : break
        except threadpool.NoResultsPending:
            print "no pending results"
            break
        except Exception ,e:
            pass
    end = datetime.datetime.now()
    print "Start at :\t" , start    
    print "End at :\t" , end
    print "Total Cost :\t" , end - start
    print 'Total url :',config.total_url
    print 'Total fetched :', config.fetched_url
    print 'Lost url :', config.total_url - config.fetched_url
    print 'Error 404 :' ,config.failed_url
    print 'Error timeout :',config.timeout_url
    print 'Error Try too many times ' ,config.trytoomany_url
    print 'Error Other faults ',config.other_url
    main.stop()
    
def writeFile(request,result):
    config.total_url += 1
    if result[1]!=None :
        config.fetched_url += 1
        print config.total_url,'\tfetched :', result[0],
    else:
        config.failed_url += 1
        print config.total_url,'\tLost :',result[0],


if __name__ =='__main__':
    try :
        import BeautifulSoup
    except Exception, e :
        print e
    usingThreadpool(config.LIMIT,config.THREAD_COUNT)
