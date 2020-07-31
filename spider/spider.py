#!/usr/bin/python3
import os, argparse, requests
packages=['pandas', 'numpy', 'lxml', 'beautifulsoup4', 'json']
log = 'begin log\n'
host='http://101.6.15.212:9503'
jwt='eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTU5NTc2MTMyN30.J9Z3zbqz-kvrBJQh-0vxkx4DvSK720As6MX6ZIIZAJB9qNhSutcWPadzSX04g6PR9M9UnyItAMtohvdgmxMD7w'
header={"Authorization": jwt, "Content-Type": "application/json"}
r = requests.get(host+'/dwf/v1/app/login?userName={}&password={}'.format('admin','123456'),
    headers=header)
# update jwt
import json
jwt = r.json()['data']
print(jwt)
parser = argparse.ArgumentParser()
header={"Authorization": jwt, "Content-Type": "application/json"}

parser.add_argument('-i', dest='oids', nargs='+',default='', help='select data oids')
args = parser.parse_args()
print(args)
log+= str(args.oids)+'\n'
'''
try:
    tempPipe = os.popen('pip3 list')
    packageList = tempPipe.read()
    tempPipe.close()
    #log += templog+'\n'
except Exception as e:
    log += e +'\n'

for package in packages: 
    if packageList.find(package)<0:
        print(package)
        try:
            tempPipe = os.popen('pip3 install {}'.format(package))
            templog = tempPipe.read()
            log += templog+'\n'
        except Exception as e:
            log += templog+'\n'

r = requests.post(host+'/dwf/v1/omf/entities/Script/objects-update',
    headers=header,
    json=[{
    "oid": "BB9F2EBEBA85B645830793ECB220AFC1",
    "outlog": log
  }])
  '''
#print(r.json()['data'])
#import pandas as pd, numpy as np
testurl = "http://tjj.sh.gov.cn/tjnj/nj19.htm?d1=2019tjnj/C0201.htm"
from bs4 import BeautifulSoup
r = requests.get(testurl,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"})
html_str = r.text
print(html_str)
exit(0)
soup = BeautifulSoup(html_str, 'lxml')
'''
if len(args.oids)==0:
    print('no select oid')
    log += 'no select oid'+'\n'
    r= requests.post(host+'/dwf/v1/omf/entities/Data/objects',
        headers=header,
        json={
            "condition" : "and obj.year>={} and obj.year<{}".format(2012, 2019)
        })
else:
    log += 'select oid:{}'.format(args.oids)+'\n'
    r= requests.post(host+'/dwf/v1/omf/entities/Data/objects',
        headers=header,
        json={
            "condition" : "and obj.oid in ({})".format(','.join(args.oids))
        })

#print(r.json())
datajson = r.json()['data']
sData = pd.read_json(json.dumps(datajson, ensure_ascii=False), orient='records')
# print(r.json()['data'])
print(sData.columns.values)
'''