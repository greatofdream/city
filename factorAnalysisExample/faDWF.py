#!/usr/bin/python3
import os, argparse, requests
packages=['pandas', 'numpy', 'sklearn', 'factor-analyzer', 'json']
log = 'begin log\n'
host='http://101.6.15.212:9503'
jwt='eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTU5NTc2MTMyN30.J9Z3zbqz-kvrBJQh-0vxkx4DvSK720As6MX6ZIIZAJB9qNhSutcWPadzSX04g6PR9M9UnyItAMtohvdgmxMD7w'
header={"Authorization": jwt, "Content-Type": "application/json"}
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

r= requests.post(host+'/dwf/v1/omf/entities/Data/objects',
    headers=header,
    json={
        "condition" : "and obj.year>={} and obj.year<{}".format(2012, 2019)
    })
import pandas as pd, numpy as np
import json
#print(r.json()['data'])
datajson = r.json()['data']
sData = pd.read_json(json.dumps(datajson, ensure_ascii=False), orient='records')
print(sData)
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
        for si in subIndicators:
            self.subIndicators[si] = 1
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
        self.economy = Indicator('Economy', ['consumeLevel','CPI','GDP'])
        self.finance = Indicator('Finance', ['socialFinancing','revenue','balanceDeposit'])#'listedCompany',
        self.education = Indicator('Education', ['undergraduateStudent','primarySchoolStudent','juniorHighSchoolStudent','seniorHighSchoolStudent','elementarySchool','secondarySchools','higherEducationSchools'])#'postgraduate',
        #self.science = Indicator('Science', ['institute','institudePeople','instituteFundamentalResearch','institudePaper','institudePatent'])
        self.health = Indicator('Health', ['medicalInstitution','medicalPeople','medicalBed'])#,'medicalCost'
        self.people = Indicator('Population', ['totalPopulation','bornRate','populationIncrease'])#,'populationAverageLife'
    def readxlsx(self, filename, sheetname=0):
        selectData = pd.read_excel(filename, sheetname, header=0, skiprows=[1], index_col=None, na_values=['NA'])
        
        self.economy.setData(selectData.loc[:, self.economy.getIndicators()])
        self.finance.setData(selectData.loc[:, self.finance.getIndicators()])
        self.education.setData(selectData.loc[:, self.education.getIndicators()])
        #self.science.setData(selectData.loc[:, self.science.getIndicators()])
        self.health.setData(selectData.loc[:, self.health.getIndicators()])
        self.people.setData(selectData.loc[:, self.people.getIndicators()])
    def setPD(self, selectData):
        self.economy.setData(selectData.loc[:, self.economy.getIndicators()])
        self.finance.setData(selectData.loc[:, self.finance.getIndicators()])
        self.education.setData(selectData.loc[:, self.education.getIndicators()])
        #self.science.setData(selectData.loc[:, self.science.getIndicators()])
        self.health.setData(selectData.loc[:, self.health.getIndicators()])
        self.people.setData(selectData.loc[:, self.people.getIndicators()])
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
        self.economy.FA()
        self.finance.FA()
        self.education.FA()
        #self.science.FA()
        self.health.FA()
        self.people.FA()
    def setDWF(self):
        self.setDWFcoeff(self.economy)
        self.setDWFcoeff(self.finance)
        self.setDWFcoeff(self.education)
        #self.setDWFcoeff(self.science)
        self.setDWFcoeff(self.health)
        self.setDWFcoeff(self.people)
    def setDWFcoeff(self, indi):
        r0 = requests.post(host+'/dwf/v1/omf/entities/PriIndi/objects',
            headers=header,
            json={
                "condition": "and obj.PriIndiName='{}'".format(indi.indicatorName)})
        priOid = r0.json()['data'][0]['oid']
        r1 = requests.post(host+'/dwf/v1/omf/entities/SubIndi/objects',
            headers=header,
            json={})
        subMap = {}
        for sm in r1.json()['data']:
            subMap[sm['SubIndiName']] = sm['oid']
        r2 = requests.post(host+'/dwf/v1/omf/relations/PriToSub/objects',
            headers=header,
            json={
                "condition": "and obj.leftOid='{}'".format(priOid)})
        relationList = r2.json()['data']
        relationMap = {}
        for rl in relationList:
            relationMap[rl['rightOid']] = rl['oid'] 
        subJson = [{
                    "oid": relationMap[subMap[si]],
                    "coeffiValue": round(indi.coeff[i][0],2),
                    "mean": round(indi.mean[i],2),
                    "sigma": round(indi.sigma[i],2)
                } for i,si in enumerate(indi.subIndicators)]
        res = requests.post(host+'/dwf/v1/omf/relations/PriToSub/objects-update',
                headers=header,
                json=subJson)
        #log += indi.PriIndiName+'\n'
        #log += res.json() +'\n'          
df = CityData()
df.setPD(sData)
df.transformToPerCapita()
df.calculateFA()
log+='end log'
r = requests.post(host+'/dwf/v1/omf/entities/Script/objects-update',
    headers=header,
    json=[{
    "oid": "BB9F2EBEBA85B645830793ECB220AFC1",
    "outlog": log
  }])
df.setDWF()





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
