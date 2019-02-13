class ScrpyerRenminRibao:
    """[summary]
    """
    import bs4

    # urlHtmlBase = "file:///home/ylin/politiqueJournalNpl/"
    urlHtmlBase = "http://paper.people.com.cn/rmrb/html/"
    urlDateBasePatten = "{year:04d}-{month:02d}/{day:02d}/"
    urlArticlePatten = "nw.D110000renmrb_{year:04d}{month:02d}{day:02d}_{num:d}-{page:02d}.htm"
    urlPagePatten = "nbs.D110000renmrb_{page:02d}.htm"

    def urlOpen(self, url, retry=3):
        import urllib.request
        import socket

        socket.setdefaulttimeout(60)
        error = ""
        for i in range(retry):
            try:
                pageRequest = urllib.request.urlopen(url)
                break
            except Exception as err:
                error = err
                print("Http Error: {0}, retry {1}, url: {2}".format(
                    err, i+1, url))
        else:
            raise error
        return pageRequest

    def getContent(self, pageRequest, retry=3):
        error = ""
        for i in range(retry):
            try:
                content = pageRequest.read().decode(
                    pageRequest.info().get_param('charset') or 'utf-8')
                break
            except Exception as err:
                error = err
                print("Http Read Error: {0}, retry {1}".format(
                    err, i+1))
        else:
            raise error

        return content

    def getUrlDateBase(self, paperDate=None):
        from datetime import datetime
        if paperDate is None:
            paperDate = datetime.now()
        dateBase = self.urlDateBasePatten.format(
            year=paperDate.year, month=paperDate.month, day=paperDate.day)

        return '{:s}{:s}'.format(self.urlHtmlBase, dateBase)

    def getArticleUrl(self, paperDate=None, page=1, num=1):
        from datetime import datetime
        if paperDate is None:
            paperDate = datetime.now()

        article = self.urlArticlePatten.format(
            year=paperDate.year, month=paperDate.month, day=paperDate.day, num=num, page=page)

        return article

    def getPageUrl(self, paperDate=None, page=1):
        from datetime import datetime
        if paperDate is None:
            paperDate = datetime.now()

        page = self.urlPagePatten.format(
            year=paperDate.year, month=paperDate.month, day=paperDate.day, page=page)

        return page

    def articleUrlToMetadata(self, url):
        import re
        from datetime import date
        from datetime import datetime

        filenameRegexp = re.compile(
            r'nw\.D110000renmrb_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_(?P<num>\d+)-(?P<page>\d{2})\.htm')
        filenameMatch = filenameRegexp.search(url)

        try:
            year = int(filenameMatch.group('year'))
            month = int(filenameMatch.group('month'))
            day = int(filenameMatch.group('day'))
            paperDate = date(year=year, month=month, day=day)
        except ValueError:
            paperDate = date.today()

        ts = datetime(year=paperDate.year, month=paperDate.month,
                      day=paperDate.day, hour=3).timestamp()

        try:
            num = int(filenameMatch.group('num'))
        except ValueError:
            pass

        try:
            page = int(filenameMatch.group('page'))
        except ValueError:
            pass

        return {
            'date': str(paperDate),
            'ts': ts,
            'page': page,
            'num': num,
            'url': url
        }

    def scrpyArticle(self, baseUrl, articleUrl):
        import bs4

        url = '{:s}{:s}'.format(baseUrl, articleUrl)

        try:
            pageRequest = self.urlOpen(url)
        except Exception as err:
            print("Http Error: {0}, give up".format(err))
            raise

        try:
            content = self.getContent(pageRequest)
        except Exception as err:
            print("Http read Error: {0}, give up".format(err))
            raise

        dom = bs4.BeautifulSoup(content, "html.parser")
        article = dom.select("#articleContent")
        title = dom.select("head > title")

        articleObj = {
            'metadata': self.articleUrlToMetadata(articleUrl),
            'title': title[0].text,
            'content': article[0].get_text(separator='\n')
        }
        return articleObj

    def scrpyPage(self, baseUrl, pageUrl):
        import bs4
        import re

        url = '{:s}{:s}'.format(baseUrl, pageUrl)

        try:
            pageRequest = self.urlOpen(url)
        except Exception as err:
            print("Http Error: {0}, give up".format(err))
            raise
        try:
            content = self.getContent(pageRequest)
        except Exception as err:
            print("Http read Error: {0}, give up".format(err))
            raise

        dom = bs4.BeautifulSoup(content, "html.parser")

        filenameRegexp = re.compile(
            r'nbs\.D110000renmrb_(?P<page>\d{2})\.htm')
        filenameMatch = filenameRegexp.search(url)
        page = 1
        if not filenameMatch is None:
            try:
                page = int(filenameMatch.group('page'))
            except ValueError:
                pass

        pageTitleDom = dom.select(
            "#ozoom > div > div.list_l > div.l_t")
        pageTitle = re.sub(r'\s', '', pageTitleDom[0].get_text())

        articlesHotzoneMap = dom.find(
            name="map", attrs={"name": "PagePicMap"})
        articles = []
        for area in articlesHotzoneMap.children:
            articleUrl = area['href']
            try:
                articles.append(self.scrpyArticle(baseUrl, articleUrl))
            except Exception as err:
                print("scrpyArticle {0}{1} failed. caused by {2}".format(
                    baseUrl, articleUrl, err))
                pass

        pageObj = {
            'metadata': {
                'page': page,
                'url': url
            },
            'title': pageTitle,
            'articles': articles
        }

        # articleUrl = '{base}/{year:04d}-{month:02d}/{day:02d}/nw.D110000renmrb_{year:04d}{month:02d}{day:02d}_{num:d}-{page:02d}.htm'.format(
        #    base=self.urlHtmlBase, year=paperdate.year, month=paperdate.month, day=paperdate.day, num=1, page=1)

        return pageObj

    def scrpyPaper(self, paperDate=None):
        import bs4
        from datetime import datetime

        if paperDate is None:
            paperDate = datetime.now()

        baseUrl = self.getUrlDateBase(paperDate=paperDate)

        url = '{:s}{:s}'.format(baseUrl, self.getPageUrl(paperDate=paperDate))

        try:
            pageRequest = self.urlOpen(url)
        except Exception as err:
            print("Http Error: {0}, give up".format(err))
            raise

        try:
            content = self.getContent(pageRequest)
        except Exception as err:
            print("Http read Error: {0}, give up".format(err))
            raise

        dom = bs4.BeautifulSoup(content, "html.parser")

        pages = []
        pagesRef = dom.select('#pageList > ul')[0].find_all(
            name="a", attrs={"id": "pageLink"})

        sumPage = len(pagesRef)
        numPage = 0
        for pageRef in pagesRef:
            # pageRef.select("#pageLink")
            numPage = numPage + 1
            print("Page {:d} of totally {:d} pages {:s}.".format(
                numPage, sumPage, str(paperDate.date())))
            try:
                pages.append(self.scrpyPage(baseUrl, pageRef['href']))
            except Exception as err:
                print("getPage {0}{1} failed. caused by {2}".format(
                    baseUrl, pageRef['href'], err))

        paperObj = {
            "pages": pages,
            "metadata": {
                "paper": "RenMinRiBao",
                "alise": ["People's daliy"],
                "ts": paperDate.timestamp(),
                "date": str(paperDate.date()),
                "scrpy_ts": datetime.now().timestamp(),
                'url': url
            }
        }

        # articleUrl = '{base}/{year:04d}-{month:02d}/{day:02d}/nw.D110000renmrb_{year:04d}{month:02d}{day:02d}_{num:d}-{page:02d}.htm'.format(
        #    base=self.urlHtmlBase, year=paperdate.year, month=paperdate.month, day=paperdate.day, num=1, page=1)

        return paperObj


def scrpyPaper(paperDate=None, pathPrefix=""):
    """[summary]
    """
    import json
    from datetime import datetime

    if paperDate is None:
        paperDate = datetime.now()

    scrpyer = ScrpyerRenminRibao()

    try:
        paperObj = scrpyer.scrpyPaper(paperDate=paperDate)
    except Exception as err:
        print("Scrpy paper {0} failed. Caused by {1}".format(
            str(paperDate.date()), err))
        raise err

    dataFileName = "RenminRibao_{0}.json".format(str(paperDate.date()))
    filePath = "{:s}{:s}".format(pathPrefix, dataFileName)
    print("Writing file {:s}".format(filePath))
    file = open(file=filePath, mode='w+', encoding='utf-8')
    try:
        json.dump(obj=paperObj, fp=file, ensure_ascii=False,
                  indent=4, sort_keys=True)
    except Exception as err:
        print(err)
        raise err
    finally:
        file.close()

    return


def strToDatetime(dateStr):
    import datetime
    ts = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
    ts = ts.replace(hour=3)
    return ts


def main():
    """[summary]
    """

    from datetime import datetime
    from datetime import timedelta
    from multiprocessing import Pool
    import argparse

    parser = argparse.ArgumentParser(description='scrpye Renmin Ribao')

    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                    help='an integer for the accumulator')
    parser.add_argument('--start', dest='start',
                        action='store', type=strToDatetime, default=None)
    parser.add_argument('--end', dest='end', action='store',
                        type=strToDatetime, default=None)
    parser.add_argument('--process', dest='process',
                        action='store', type=int, default=16)
    parser.add_argument('--path', dest='path', action='store', default='./')
    args = parser.parse_args()

    if args.start is None:
        if args.end is None:
            start = datetime.now()
            end = datetime.now()
        else:
            start = args.end
            end = args.end
    else:
        if args.end is None:
            start = args.start
            end = args.start
        else:
            start = args.start
            end = args.end
    end.replace(hour=23)

    # pathPrefix = '/home/ylin/host_home/RenminRibaoTest/'
    pathPrefix = args.path

    if not pathPrefix[len(pathPrefix)-1] == '/':
        pathPrefix = pathPrefix + '/'

    process = args.process

    print("[{ts}] Start scrpy Renmin Ribao from {start} to {end} to {pathPrefix:s} with {process:d} processes.".format(
        ts=datetime.now(), start=start, end=end, pathPrefix=pathPrefix, process=process))

    # make thread config map
    now = start
    dateList = []
    while now <= end:
        dateList.append(now)
        now = now + timedelta(days=1)

    print('Dates in task :')
    for paperDate in dateList:
        print(str(paperDate.date()), end=',\t')
    print('')

    pool = Pool(process)
    for paperDate in dateList:
        pool.apply_async(func=scrpyPaper, args=(paperDate, pathPrefix))

    pool.close()
    pool.join()
    print("[{ts}] All processes joined. Big brother is watching you".format(
        ts=datetime.now()))

    return


if __name__ == '__main__':
    main()
