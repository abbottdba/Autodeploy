from urllib import parse,request
import json, time, hashlib

time_stamp = time.time()
token = hashlib.md5(str('NEBB5oMQOPMpLTn6PneJKBDEMU0WeBxd' + str(int(time_stamp))).encode('utf-8')).hexdigest()

def api_post(page):
    textmod={"option": "querybytype", "parameters": {"data": ["CloudServer"], "page": page, "limit": 20}, "token": token, "timestamp": str(int(time_stamp))}
    textmod = json.dumps(textmod).encode(encoding='utf-8')
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',"Content-Type": "application/json"}
    url='http://cmdb.omtools.me/api/assets/'
    req = request.Request(url=url,data=textmod,headers=header_dict)
    res = request.urlopen(req)
    res = res.read()
    return json.loads(res.decode(encoding='utf-8'))

def push_file(asset_data):
    f = open('asset.data', 'w')
    for business_name, data_dic in asset_data.items():
        f.write('%s\n%s\n%s\n\n' % (business_name, data_dic['admin'], '\n'.join(ip for ip in data_dic['ip']) ))
    f.close()

def fetch_data():
    page = 1
    group_data = {}
    while True:
        json_data = api_post(page)
        if json_data.get('data'):
            for obj in json_data.get('data'):
                if obj['status'] == 'Active':
                    if not group_data.get('%s-%s' % (obj['business'], obj['function'][0])):
                        group_data['%s-%s' % (obj['business'], obj['function'][0])] = {'ip': []}
                    group_data['%s-%s' % (obj['business'], obj['function'][0])]['ip'].append(obj['ip'])
                    group_data['%s-%s' % (obj['business'], obj['function'][0])]['admin'] = obj['admin']
            page += 1
        else:
            break
    return group_data

if __name__ == '__main__':
    data = fetch_data()
    push_file(data)