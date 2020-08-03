//npm install -g cnpm --registry=https://registry.npm.taobao.org
const puppeteer = require('puppeteer');
const process = require('process');
// const {TimeoutError} = require('puppeteer/Errors');
// node spider.js  http://tjj.sh.gov.cn/tjnj/nj19.htm?d1=2019tjnj/C0201.htm
var url = process.argv[2]
console.log(url)
if (url===null){
  console.log('please use: node spider.js url')
  exit(0)
}
async function dumpFrameTree(frame, indent) {
  //var text = await frame.content();
  var text = await frame.$$('table')
  if (text.length>0){
    console.log(indent + frame.url());
    //var xtext = await frame.$eval('table', x=>x.outerHTML)
    //console.log(xtext)
    for (let i =0;i<text.length;i++){
      const x = await text[i].$$('tr')
      for(let j=0;j<x.length;j++){
        var xtext = await x[j].$$eval('td',es=>{
          return es.map(e=>e.innerHTML)
        })
        console.log(xtext)
      }
    }
  }
  for (let child of frame.childFrames())
    await dumpFrameTree(child, indent + '  ');
}
async function spider(url){
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(url, waitUntil='networkidle0');
  // Spage.once('load', ()=>{console.log('load')});
  // await page.screenshot({path: './example.png'});
  //await page.screenshot({path: './example.png'}).then(()=>{console.log('save png')})
  await page.waitForSelector('frame')
  //const html = await page.content()
  //console.log(html)
  //console.log(page.frames())
  const frame = page.mainFrame();
  await dumpFrameTree(frame, ' ')
  /*try{
    await page.waitForSelector('table').then(async ()=>{  
        console.log('get html')
        const html = await page.content();
        console.log(html)
        const tableArray = await page.$$('table');
        console.log(tableArray)
        await browser.close();
      } 
    )}catch (e) {
    console.log('get element Error'+e)
    await browser.close();
  };*/
  await browser.close()
  // await page.pdf({path:'./example.pdf', format:'A4'})
};
spider(url);