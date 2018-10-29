
import sys, os, getopt, urllib, json
import urllib.request
import shutil
import tempfile
import hashlib
import zipfile




def calculate_hash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class MorphoSource:        
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.Host = 'www.morphosource.org'
        self.User_Agent =  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
        self.Accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.Accept_Language = 'en-US,en;q=0.5'
        self.Accept_Encoding = 'gzip, deflate, br'
        self.Content_Type = 'application/x-www-form-urlencoded'
        self.Content_Length: '93'
        self.Cookie = None
        self.Connection = 'keep-alive'
        self.Upgrade_Insecure_Requests = '1'
        self.__getCookieFromMainPage()
        self.__login()

    def __getCookieFromMainPage(self):
        url = 'https://www.morphosource.org/'
        params = {}
        data =  urllib.parse.urlencode(params).encode('utf8')
        headers = {'User-Agent': self.User_Agent}
        headers['Host'] = self.Host
        headers['Content-Type'] = self.Content_Type
        req = urllib.request.Request(url, data, headers)
        cookie = None
        self.Cookie = None
        with urllib.request.urlopen(req) as response:
            info = response.info()
            for c in info["Set-Cookie"].split(';'):
                if c.startswith("morphosource="):
                        cookie = c
                        self.Cookie = c
        if self.Cookie == None:
            raise ValueError('unable to retrieve cookie')


    def __login(self):
        url = 'https://www.morphosource.org/LoginReg/login'
        params = {'username' : self.username, 'password':self.password }
        data =  urllib.parse.urlencode(params).encode('utf8')
        headers = {'User-Agent': self.User_Agent}
        headers['Host'] = self.Host
        headers['Referer'] =  'https://www.morphosource.org/LoginReg/form'
        headers['Content-Type'] = self.Content_Type
        headers['Cookie'] = self.Cookie
        req = urllib.request.Request(url, data, headers)
        with urllib.request.urlopen(req) as response:
             info = response.info()
             s = response.read()
             if "Login failed." in str(s) :
                raise ValueError('Invalid username and/or password') 
    
    def getMedia(self, media_id, media_file_id, outputDir):
        url = 'https://www.morphosource.org/Detail/MediaDetail/DownloadMedia'
        params = {'3d_print':'0', 'download' : '1', 'intended_use_other' : 'oVert partner', 'media_id':media_id, 'media_file_id':media_file_id }
        data =  urllib.parse.urlencode(params).encode('utf8')
        headers = {'User-Agent': self.User_Agent}
        headers['Host'] =self. Host
        headers['Content-Type'] = self.Content_Type
        headers['Referer'] =  'https://www.morphosource.org/Detail/MediaDetail/Show/media_id/' + media_id
        headers['Cookie'] = self.Cookie
        req = urllib.request.Request(url, data, headers)
        filename = None
        with urllib.request.urlopen(req) as response:
            info = response.info()
            filename = os.path.join(outputDir, info["Content-Disposition"].replace('attachment; filename=',''))
            with open(filename, 'wb') as the_file:
                shutil.copyfileobj(response, the_file)
        return filename

def showHelp():
    print('msinjestr.py -u <usename> -p <password> -o <output folder> -m <media id> -f <media file id>')
    sys.exit()


if __name__ == "__main__":
    username = None
    password = None
    outputDir = ''
    mediaId = None
    mediaFileId = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:o:m:f:h')
    except getopt.GetoptError as err:
        print(err)
        print('invalid args, for help: msinjestr.py -h')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            showHelp()
        elif opt == '-u':
            username = arg
        elif opt == '-p':
            password = arg
        elif opt == '-o':
            outputDir = arg
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
        elif opt == '-m':
            mediaId = arg
        elif opt == '-f':
            mediaFileId = arg
        elif opt == '-h':
            showHelp()
            sys.exit()
        else:
            raise ValueError('unhandled option') 
    
    if mediaId == None or mediaFileId == None:
        showHelp()
        sys.exit()
    try:
        ms = MorphoSource(username,password)
    except ValueError as e:
        print(e)
        sys.exit()
    try:    
        zfilename = ms.getMedia(mediaId, mediaFileId, outputDir)
    except ValueError as e:
        print(e)
        sys.exit()

    print (zfilename)
    z = zipfile.ZipFile(zfilename, 'r')
    extractToDir = os.path.join(outputDir, os.path.splitext(zfilename)[0])
    z.extractall(extractToDir)
    z.close()
    for filename in os.listdir(extractToDir):
        print(calculate_hash(os.path.join(extractToDir, filename)), " : ", filename)




