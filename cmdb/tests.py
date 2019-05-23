from urllib import parse,request
import json, time, hashlib

time_stamp = time.time()
token = hashlib.md5(str('NEBB5oMQOPMpLTn6PneJKBDEMU0WeBxd' + str(int(time_stamp))).encode('utf-8')).hexdigest()

textmod={"option": "querybybusiness", "parameters": {"data": ["ertyert_yerq"], "page": 1, "limit": 120}, "token": token, "timestamp": str(int(time_stamp))}
print(textmod)
textmod = json.dumps(textmod).encode(encoding='utf-8')
header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',"Content-Type": "application/json"}
url='http://127.0.0.1:8001/api/assets/'
req = request.Request(url=url,data=textmod,headers=header_dict)
res = request.urlopen(req)
res = res.read()
print(res)
print(res.decode(encoding='utf-8'))