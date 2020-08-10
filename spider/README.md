# 爬虫脚本介绍
## 安装流程
https://nodejs.org/en/download/
这里下载node

npm init初始化一个`package.json`存放依赖

安装淘宝提供的npm工具cnpm加速
npm install -g cnpm --registry=https://registry.npm.taobao.org

然后clone仓库，我新建了一个spider的文件夹，写了一个可以截屏的脚本，到那个文件夹
npm install puppeteer --save

会自动下载一个chromenium

然后node spider.js执行脚本

## run
node dwfaxios.js http://tjj.sh.gov.cn/tjnj/nj19.htm?d1=2019tjnj/C0201.htm 2 '6A6CE37092D49344B9C9BCBBF9EFE725' 'populationAverageLife'
## 爬虫核心代码
爬虫使用nodejs脚本，依赖包括`puppeteer`,`axios`。选用`puppeteer`可以模拟浏览器行为，执行动态脚本，年鉴网页中需要动态加载iframe，因此不能用普通的静态获取并解析网页的库，如`cheerio`和`BeautifulSoup`。

`puppeteer`构造一个浏览器对象`browser`，在`browser`中加载对应年鉴网页的`url`。年鉴网页中包含的`HTML`元素是嵌套的`Iframe`,`browser`递归的搜索`Iframe`，将包含有表格`<table>`的`Iframe`选择出来。

之后校验表格开头的字符串，以`年`开头行视为表头，之后向后续搜索数据。校验到第一个字符串为`19`或者`20`开头，那么即为数据行，对于每一行按照`<td>`标签进行循环，取出`<td>`标签其中的属性值`x:num`（该属性是由excel转换后的表格特有的）。将选择出的某列值和年份构成`map`，重新写入数据库。