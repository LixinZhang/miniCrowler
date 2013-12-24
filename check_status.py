import os

f = {}

filelist = os.listdir(os.getcwd()+'/pages/')
for fi in filelist :
    try :
        fi = fi.split('-')[0]
        k = fi.index('.')
        fi = fi[k+1:]
        if f.get(fi,None) == None :
            f[fi] = 1
        f[fi] +=1
    except Exception , ex :
        pass
arr = []
for key in f :
    arr.append((f[key],key))

import os 
os.system('du -h --max-depth=1 pages/')

print 'Rank\t\tHostname\tTimes\t'
print '-' * 40
top = 0
arr.sort(reverse=True)
for times, hostname in arr :
    top += 1
    print '%4d\t%20s\t%6d\t' % (top, hostname, times)
    if top > 20 : break
