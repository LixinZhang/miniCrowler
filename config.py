timeout = 5
fetched_url = 0
failed_url = 0
timeout_url = 0
trytoomany_url =0
other_url = 0
max_try_times = 3
total_url = 0

RESULTOTHER = 0 #Other faults
RESULTFETCHED = 1 #success
RESULTCANNOTFIND = 2 #can not find 404
RESULTTIMEOUT = 3 #timeout
RESULTTRYTOOMANY = 4 #too many tries

DOWNLOAD_STORAGE_FOLDER = 'pages/'
CRAWLER_NAME = 'minicrawler_buaa'
SEED_FILE = 'input.txt'

THREAD_COUNT = 10
LIMIT = 30000
