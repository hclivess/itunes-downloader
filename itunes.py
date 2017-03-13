import socket, threading, time, log_handling, requests, re, os.path, glob, logging, sys
from logging.handlers import RotatingFileHandler

#logging
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = str(time.time())+'.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(funcName)s(%(lineno)d) %(message)s')
ch.setFormatter(formatter)
app_log.addHandler(ch)
#logging

max_threads = 2
max_threads = max_threads + 1 #include parent

if not os.path.exists("temp"):
    os.makedirs("temp")

f = open('list.plist', 'r')
libraries = re.findall("(https\:\/\/.*)\<", f.read())
libraries = list(set(libraries))
#print libraries

def slugify(value):
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value

def download_file(url,title,ext,i,album):
    if not os.path.exists("temp\\" + album):
        os.makedirs("temp\\" + album)

    path_target = album+"\\"+title+ext
    path_temp = "temp\\"+album+"\\"+title+ext

    try:

            if not os.path.isfile(path_target):
                print("downloading "+str(path_target))

                r = requests.get(url, stream=True, headers=hdr)

                if os.path.isfile(path_temp):
                    os.remove(path_temp)
                    
                with open(path_temp, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024): 
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)

                if not os.path.exists(album):
                    os.makedirs(album)
                os.rename(path_temp,path_target)

                try:
                    os.rmdir("temp\\"+album+"\\")
                    print "temp removed"
                except:
                    print "temp not removed, not empty"
                    pass

            else:
                print(str(title) + " already downloaded")

    except Exception, e:
        app_log.info(str(e)+" "+str(album)+" "+str(url)+" "+str(title)+" "+str(ext)+" "+str(i))
        
# timeout in seconds
timeout = 6
socket.setdefaulttimeout(timeout)
# timeout in seconds
# set header
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Accept-Encoding': 'gzip, deflate, sdch',
       'Accept-Language': 'cs,sk;q=0.8,en;q=0.6,en-GB;q=0.4',
       'Connection': 'keep-alive'}
# set header

for root in libraries:
    try:
        request = requests.get(root, headers=hdr)

        geturl_readable = request.text
        links = re.findall("enclosure url=\"(.*)\?", geturl_readable)
        titles = re.findall("\<title\>(.*)\<", geturl_readable)

        exts = re.findall("(\.\w+)\?", geturl_readable)

        titles = [slugify(x) for x in titles]

        album = titles[0]
        titles.pop(0)

        i=0
        for x in links:
            try:
                while threading.activeCount() >= max_threads:
                    print "waiting for free threads: "+str(threading.activeCount())+" / "+str(max_threads)
                    time.sleep(1)

                print "thread started"
                t = threading.Thread(target=download_file, args=(x,titles[i], exts[i], i, album))  # threaded connectivity to nodes here
                t.start()
                i = i+1
            except Exception, e:
                app_log.info(e)
                pass

    except Exception, e:
        app_log.info(e)
        pass
