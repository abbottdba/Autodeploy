import time, sys, datetime, re
import dns.resolver
import queue
import threading

from urllib import parse, request
import json, time, hashlib
import settings


class DnsMonitorHandler:
    def __init__(self):
        self.api_post_url = settings.api_post_url
        self.data_api = settings.data_api
        self.domain_data = self.domain_data_from_api()
        self.app_map = {
            'XBET': 'XBET',
            'BBET8': 'BBET8',
            'RUIBO': 'RUIBO',
            'BBETASIA': 'BBETASIA',
            'BOLEBA / JINSHENG': 'JINSHENG',
            'EU': 'EU',
            'HAOMEN': 'HAOMEN',
            'JINSHENG / TIANHE': 'TIANHE',
        }

    def domain_data_from_api(self):
        from urllib import parse, request
        import json, time, hashlib

        time_stamp = time.time()
        token = hashlib.md5(str('NEBB5oMQOPMpLTn6PneJKBDEMU0WeBxd' + str(int(time_stamp))).encode('utf-8')).hexdigest()

        textmod = {"option": "querybydomain", "parameters": {"data": "all", "page": 1, "limit": 120},
                   "token": token, "timestamp": str(int(time_stamp))}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                       "Content-Type": "application/json"}
        req = request.Request(url=self.data_api, data=textmod, headers=header_dict)
        res = request.urlopen(req)
        res = res.read()

        return json.loads(res.decode(encoding='utf-8'))

    def write_record(self, data):
        f = open('domain.log', 'a')
        f.write('%s\n' % data)
        f.close()

    def __api_post(self, domain, pro_name):
        if self.app_map.get(pro_name):
            app_name = self.app_map.get(pro_name)
            print('-----------------', app_name)
            textmod = {"domain": domain, "node": 1, 'pro_name': app_name}

            textmod = json.dumps(textmod).encode(encoding='utf-8')
            header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                           "Content-Type": "application/json"}
            req = request.Request(url=self.api_post_url, data=textmod, headers=header_dict)
            res = request.urlopen(req)
            res = res.read()
            print(res)
            #print(res.decode(encoding='utf-8'))

    def __ip_check(self, ip_addr=""):
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", ip_addr):
            return True
        else:
            return False

    def __exec_check(self, pro_name, domain_list, ip_list):
        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = ['114.114.114.114']
        for domain in domain_list:
            str_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                A = my_resolver.query(domain, 'A')
                for i in A.response.answer:
                    for j in i.items:
                        if self.__ip_check(str(j)):
                            if str(j) not in ip_list:
                                print('--------------------')
                                self.write_record('Check diffrent: %s, %s - %s' % (domain, j, str_time))
                                self.__api_post(domain, pro_name)
                                print(pro_name, domain)
                            else:
                                print(domain)
                time.sleep(3)
            except KeyboardInterrupt:
                sys.exit()
            except:
                print('--------------------')
                self.write_record('Check error: %s - %s' % (domain, str_time))

    def main(self):
        threading_pool = []
        for pro_name, data in self.domain_data.items():
            th = threading.Thread(target=self.__exec_check, args=(pro_name, data['domain_list'], data['ip_list']))
            threading_pool.append(th)

        for th in threading_pool:
            th.start()
        for th in threading_pool:
            th.join()


if __name__ == '__main__':
    dns_handler = DnsMonitorHandler()
    dns_handler.main()