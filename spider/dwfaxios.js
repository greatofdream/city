var http = require("http")
var querystring =  require("querystring")
var axios = require('axios')
const puppeteer = require('puppeteer');
const process = require('process');
// argv process
var url = process.argv[2]
var column = parseInt(process.argv[3])
var oid = process.argv[4]//'6A6CE37092D49344B9C9BCBBF9EFE725'
var attr = process.argv[5]//'populationAverageLife'
// parameter control
var findHeader = false;
var findData = false;
let datamap = new Map();
// spider on the web
if (url===null){
    console.log('please use: node spider.js url')
    exit(0)
  }
async function dumpFrameTree(frame, indent) {
    var tables = await frame.$$('table')
    if (tables.length>0){
      console.log(indent + frame.url());
      for (let i =0;i<tables.length;i++){
        if(i>2){
          console.log('scan two tables, Abort')
          break
        }
        const x = await tables[i].$$('tr')
        // search the table
        for(let j=0;j<x.length;j++){
          var xtext = await x[j].$$eval('td',es=>{
            return es.map(e=>{
              if (e.getAttribute("x:num")===''|e.getAttribute("x:num")===null){
                return e.innerHTML;
              }else{
                return e.getAttribute("x:num")
              }
            })
          })
          if(xtext.length>1&xtext[0]!=''){
            if(!findHeader&(xtext[0].indexOf("年")>=0|xtext[0].indexOf("year")>=0)){
              console.log('find the header; begin to look for data until the second table')
              findHeader = true
              console.log(xtext)
            }
            if(!findData&(xtext[0].indexOf('20')==0|xtext[0].indexOf('19')==0)){
              console.log('find the data part')
              findData = true
            }
            if(findData){
              datamap.set(Number(xtext[0]), Number(xtext[column]))
            }
          }
        }
      }
    }
    if(findData){
      return;
    }
    for (let child of frame.childFrames())
      await dumpFrameTree(child, indent + '  ');
}
async function spider(url){
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url, waitUntil='networkidle0');
    await page.waitForSelector('frame')
    const frame = page.mainFrame();
    await dumpFrameTree(frame, ' ')
    await browser.close()
};

// const info of server
const host ='http://101.6.15.212:9503'
const port = 9503
var jwt='eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTU5NTc2MTMyN30.J9Z3zbqz-kvrBJQh-0vxkx4DvSK720As6MX6ZIIZAJB9qNhSutcWPadzSX04g6PR9M9UnyItAMtohvdgmxMD7w'
var header={"Authorization": jwt, "Content-Type": "application/json"}
var dataList, postData;

async function getPostData(){
		console.log('begin spider')
		await spider(url)
		console.log('end spider')
    // get token
    var jwtRes = await axios.get(host+'/dwf/v1/app/login?userName=admin&password=abc123',{headers:header})
    var jwt = jwtRes.data.data
    var header={"Authorization": jwt, "Content-Type": "application/json"}
    console.log(jwt)
    // use city oid get data oid
    var dataRes = await axios.post(host+'/dwf/v1/omf/entities/Data/objects', data={"condition":"and obj.cityOid='"+oid+"'"}, {headers:header}).catch(e=>{
        console.log(e)
		})
    var timedata = dataRes.data.data
		for(let i=0;i<timedata.length;i++){
			if (datamap.get(timedata[i].year)!=undefined){
				timedata[i][attr] = datamap.get(timedata[i].year)
				console.log(timedata[i])
			}
		}
		//console.log(timedata)
		var updatedata = await axios.post(host+'/dwf/v1/omf/entities/Data/objects-update',data=timedata, {headers:header}).catch(e=>{
        console.log(e)
		})
		console.log(updatedata)
		console.log('end the post process')
}
getPostData();