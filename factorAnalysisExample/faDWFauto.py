#!/usr/bin/python3
import os, argparse, requests
packages=['pandas', 'numpy', 'sklearn', 'factor-analyzer']
log = 'begin log\n'
host='http://101.6.15.212:9503'
jwt='eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTU5NTc2MTMyN30.J9Z3zbqz-kvrBJQh-0vxkx4DvSK720As6MX6ZIIZAJB9qNhSutcWPadzSX04g6PR9M9UnyItAMtohvdgmxMD7w'
header={"Authorization": jwt, "Content-Type": "application/json"}
r = requests.get(host+'/dwf/v1/app/login?userName={}&password={}'.format('admin','abc123'),
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

try:
    tempPipe = os.popen('pip3 list')
    packageList = tempPipe.read()
    tempPipe.close()
    #log += templog+'\n'
except Exception as e:
    log += e +'\n'
'''
for package in packages: 
    if packageList.find(package)<0:
        print(package)
        try:
            tempPipe = os.popen('pip3 install {}'.format(package))
            templog = tempPipe.read()
            log += templog+'\n'
        except Exception as e:
            log += templog+'\n'
'''
r = requests.post(host+'/dwf/v1/omf/entities/Script/objects-update',
    headers=header,
    json=[{
    "oid": "BB9F2EBEBA85B645830793ECB220AFC1",
    "outlog": log
  }])
#print(r.json()['data'])
import pandas as pd, numpy as np

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

r = requests.post(host+'/dwf/v1/omf/entities/Script/objects-update',
    headers=header,
    json=[{
    "oid": "BB9F2EBEBA85B645830793ECB220AFC1",
    "outlog": log
  }])
from sklearn.datasets import  load_iris
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo

class Indicator(object):
    def __init__(self, name, subIndicators):
        self.indicatorName = name
        self.subIndicators = {}
        self.indiIndexMap = {}
        for si in subIndicators:
            self.subIndicators[si] = 1
        for i, si in enumerate(self.subIndicators.keys()):
            self.indiIndexMap[si] = i
    def getIndicators(self):
        return self.subIndicators.keys()
    def setData(self, timeData):
        self.timeData = timeData
        self.rawdf = self.timeData.fillna(method='ffill', axis=0).fillna(method='bfill', axis=0)
        self.mean = self.rawdf.mean()
        self.sigma = self.rawdf.std()
        #self.df = (self.rawdf-self.mean)/self.sigma
        #factor_analyzer standardizes input data automatically, so manual standardization is not necessary.
        self.df = self.rawdf * 1
    def FA(self):
        fa = FactorAnalyzer(n_factors=1, method="principal", rotation="varimax")
        fa.fit(self.df)
        # Print eigenvalues
        ev, v = fa.get_eigenvalues()
        print(ev)
        # Print loadings
        print(fa.loadings_)
        self.coeff = fa.loadings_
        return 0
    def PCA(self):
        return 0
    def renewMeanAndSigma(self):
        #Used to re-calculate mean and sigma after transformToPerCapita()
        self.mean = self.df.mean()
        self.std = self.df.std()
        
class CityData(object):
    def __init__(self):
        self.EnglishName = ''
        self.ChineseName = ''
        self.cityOid = ''
        self.economy = Indicator('Economy', ['CPI','GDP'])
        self.finance = Indicator('Finance', ['socialFinancing','revenue','balanceDeposit'])#'listedCompany',
        self.education = Indicator('Education', ['undergraduateStudent','primarySchoolStudent','juniorHighSchoolStudent','seniorHighSchoolStudent','elementarySchool','secondarySchools','higherEducationSchools'])#'postgraduate',
        #self.science = Indicator('Science', ['institute','institudePeople','instituteFundamentalResearch','institudePaper','institudePatent'])
        self.health = Indicator('Health', ['medicalInstitution','medicalPeople','medicalBed'])#,'medicalCost'
        self.people = Indicator('Population', ['totalPopulation','bornRate','populationIncrease'])#,'populationAverageLife'
    def __init__(self, priIndi, relation):
        self.priIndi = priIndi
        self.priLength = len(priIndi)
        self.relation = relation
        self.listIndi = []
        self.indiIndexMap = {}
        for i, pi in enumerate(priIndi):
            self.listIndi.append(Indicator(pi, relation[pi]))
            self.indiIndexMap[pi] = i
    def setPD(self, selectData):
        for i in range(self.priLength):
            self.listIndi[i].setData(selectData.loc[:, self.listIndi[i].getIndicators()])
    def transformToPerCapita(self):
        #Transform some sub-indicators to per capita
        
        #First, extract the totalPopulation data
        popCol = self.people.df['totalPopulation']
        
        #Second, divide particular data by totalPopulation
        
        #economy
        tmpSubIndi = ['GDP']
        self.economy.df[tmpSubIndi] = self.economy.df[tmpSubIndi].div(popCol, axis=0)
        
        #finance
        tmpSubIndi = ['socialFinancing', 'revenue', 'balanceDeposit']
        self.finance.df[tmpSubIndi] = self.finance.df[tmpSubIndi].div(popCol, axis=0)
        
        #education
        tmpSubIndi = ['undergraduateStudent', 'primarySchoolStudent', 'juniorHighSchoolStudent', 
                      'seniorHighSchoolStudent', 'elementarySchool', 'secondarySchools', 
                      'higherEducationSchools']
        self.education.df[tmpSubIndi] = self.education.df[tmpSubIndi].div(popCol, axis=0)
        
        #science
        #tmpSubIndi = []
        #self.science.df[tmpSubIndi] = self.science.df[tmpSubIndi].div(popCol, axis=0)
        
        #health
        tmpSubIndi = ['medicalInstitution', 'medicalPeople', 'medicalBed']
        self.health.df[tmpSubIndi] = self.health.df[tmpSubIndi].div(popCol, axis=0)
        
        #people
        #tmpSubIndi = []
        #self.people.df[tmpSubIndi] = self.people.df[tmpSubIndi].div(popCol, axis=0)
        
        #Third, re-calculate mean and sigma
        self.economy.renewMeanAndSigma()
        self.finance.renewMeanAndSigma()
        self.education.renewMeanAndSigma()
        #self.science.renewMeanAndSigma()
        self.health.renewMeanAndSigma()
        self.people.renewMeanAndSigma()   
    def calculateFA(self):
        for i in range(self.priLength):
            self.listIndi[i].FA()
    def setDWF(self, relation, priIndiOids, subIndiOids):
        subJson = []
        for rl in relation:
            priName = priIndiOids[rl['leftOid']]
            subName = subIndiOids[rl['rightOid']]
            priIndex = self.indiIndexMap[priName]
            subIndex = self.listIndi[self.indiIndexMap[priName]].indiIndexMap[subName]
            subJson.append({
                "oid": rl['oid'],
                "coeffiValue": round(self.listIndi[priIndex].coeff[subIndex][0],2),
                "mean": round(self.listIndi[priIndex].mean[subIndex],2),
                "sigma": round(self.listIndi[priIndex].sigma[subIndex],2)
            })
        res = requests.post(host+'/dwf/v1/omf/relations/PriToSub/objects-update',
                headers=header,
                json=subJson)
# get priIndi and subIndi map
r0 = requests.post(host+'/dwf/v1/omf/entities/PriIndi/objects',
    headers=header,
    json={
        "condition": ""})
# storage (oid,priIndi)
priIndiOids = {}
for pio in r0.json()['data']:
    priIndiOids[pio['oid']] = pio['PriIndiName']

print(priIndiOids)
# subindis
r2 = requests.post(host+'/dwf/v1/omf/entities/SubIndi/objects',
    headers=header,
    json={
        "condition": ""})
# storage (oid,subIndi)
subIndiOids = {}
divSubIndi = ['TotalRetailSalesofConsumerGoods', 'TotalImportsandExports', 'GDP', 'TotalWasteWater', 'LoansInFinanInsititutions', 'DepositsInFinanInsititutions', 'revenue', 
        'undergraduateStudent', 'primarySchoolStudent', 'juniorHighSchoolStudent', 'seniorHighSchoolStudent', 'elementarySchool', 'secondarySchools', 
        'higherEducationSchools', 'medicalInstitution', 'medicalPeople', 'medicalBed']
for sio in r2.json()['data']:
    subIndiOids[sio['oid']] = sio['SubIndiName']

# storage priIndi
priIndis = priIndiOids.values()
r1 = requests.post(host+'/dwf/v1/omf/relations/PriToSub/objects',
    headers=header,
    json={
        "condition": ""})
# storage (priIndi:[subIndi])
priIndiMap = {}
for i in priIndis:
    priIndiMap[i] = []
for rl in r1.json()['data']:
    priIndiMap[priIndiOids[rl['leftOid']]].append(subIndiOids[rl['rightOid']]) 
print(priIndiMap)
df = CityData(priIndis, priIndiMap)
# transfromToPerCapita directly
sData[divSubIndi] = sData[divSubIndi].div(sData['totalPopulation'], axis=0)
df.setPD(sData)
# df.transformToPerCapita(sData['totalPopulation'])
df.calculateFA()
log+='end log'
r = requests.post(host+'/dwf/v1/omf/entities/Script/objects-update',
    headers=header,
    json=[{
    "oid": "BB9F2EBEBA85B645830793ECB220AFC1",
    "outlog": log
  }])
df.setDWF(r1.json()['data'], priIndiOids, subIndiOids)





# write the log to dataset

r = requests.post(host+'/dwf/v1/omf/entities/Script/objects-update',
    headers=header,
    json=[{
    "oid": "BB9F2EBEBA85B645830793ECB220AFC1",
    "outlog": log
  }])
#print(r.content)
#psr = argparse.ArgumentParser()
#psr.add_argument('-i', dest='indicator', nargs='+', help='indicator type')
