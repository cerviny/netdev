import requests,urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FortiGate:
    def __init__(self, ipaddr, username, password, path, timeout=10, port='443', verify=False):

        self.ipaddr = ipaddr
        self.username = username
        self.password = password
        self.port = port
        self.urlbase = 'https://{ipaddr}:{port}/'.format(ipaddr=self.ipaddr, port=self.port)
        self.timeout = timeout
        self.verify = verify
        self.path = path
        self.session = requests.session()

    def get(self, url):

        request = self.login().get(url, verify=self.verify, timeout=self.timeout)
        self.logout()
        if request.status_code == 200:
            return request
        else:
            return request.status_code

    def login(self):

        url = self.urlbase + 'logincheck'

        self.session.post(url,
                          data='username={username}&secretkey={password}'.format(username=self.username,
                                                                                 password=self.password),
                          verify=self.verify,
                          timeout=self.timeout)

        for cookie in self.session.cookies:
            if cookie.name == 'ccsrftoken':
                csrftoken = cookie.value[1:-1]
                self.session.headers.update({'X-CSRFTOKEN': csrftoken})

        return self.session

    def logout(self):

        url = self.urlbase + 'logout'
        self.session.get(url, verify=self.verify, timeout=self.timeout)

    def save(self):
        result = self.backup()
        with open('%s/%s.txt' % (self.path, self.ipaddr), 'wb') as f:
            for line in result:
                f.write(line)

    def backup(self):
        api_url = self.urlbase + 'api/v2/monitor/system/config/backup?scope=global'
        results = self.get(api_url)
        return results
