//npm install -g cnpm --registry=https://registry.npm.taobao.org
const puppeteer = require('puppeteer');
const process = require('process');
// node spider.js  http://tjj.sh.gov.cn/tjnj/nj19.htm?d1=2019tjnj/C0201.htm
var url = process.argv[2]
console.log(url)
if (url===null){
  console.log('please use: node spider.js url')
  exit(0)
}
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(url);
  await page.screenshot({path: './example.png'});
  // await page.pdf({path:'./example.pdf', format:'A4'})
  await browser.close();
})();