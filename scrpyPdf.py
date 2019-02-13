def downloadFile(url, path, retry=3, timeout=120):
    import urllib.request
    import shutil
    import socket

    socket.setdefaulttimeout(60)
    error = ""
    for i in range(retry):
        try:
            # Download the file from `url` and save it locally under `file_name`:
            with urllib.request.urlopen(url) as response, open(path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
        except Exception as err:
            error = err
            print("Http Error: {0}, retry {1}, url: {2}".format(
                err, i+1, url))
    else:
        raise error

    return


def getPageUrl(paperDate, page):
    # 'http://paper.people.com.cn/rmrb/page/2018-03/26/01/rmrb2018032601.pdf'
    baseUrl = "http://paper.people.com.cn/rmrb/page/"
    pageFile = "{year:04d}-{month:02d}/{day:02d}/{page:02d}/rmrb{year:04d}{month:02d}{day:02d}{page:02d}.pdf".format(
        year=paperDate.year, month=paperDate.month, day=paperDate.day, page=page
    )
    url = '{}{}'.format(baseUrl, pageFile)
    return url


def getPagePath(paperDate, page, basePath=""):
    pageFile = "rmrb{year:04d}{month:02d}{day:02d}{page:02d}.pdf".format(
        year=paperDate.year, month=paperDate.month, day=paperDate.day, page=page
    )
    url = '{}{}'.format(basePath, pageFile)
    return url


def unitAndCompress(paperDate, pathPrefix=""):
    import os

    dirpath = '{prefix:s}{year:04d}/{month:02d}/{day:02d}/'.format(
        prefix=pathPrefix, year=paperDate.year, month=paperDate.month, day=paperDate.day)

    tempFile = '{prefix:s}{year:04d}/{month:02d}/temp-rmrb{year:04d}{month:02d}{day:02d}.pdf'.format(
        prefix=pathPrefix, year=paperDate.year, month=paperDate.month, day=paperDate.day)

    dstFile = '{prefix:s}{year:04d}/{month:02d}/rmrb{year:04d}{month:02d}{day:02d}.pdf'.format(
        prefix=pathPrefix, year=paperDate.year, month=paperDate.month, day=paperDate.day)

    os.system(
        "pdfunite {dirpath}*.pdf {tempFile} >/dev/null 2>&1".format(dirpath=dirpath, tempFile=tempFile))

    os.system("gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile={output} {input} >/dev/null 2>&1".format(
        output=dstFile, input=tempFile))

    os.system("rm {temp}  >/dev/null 2>&1".format(temp=tempFile))

    return


def scrpyPaper(paperDate=None, pathPrefix=""):
    """[summary]
    """
    print("Getting paper pdf {}".format(paperDate.date()))
    import os
    from datetime import datetime

    for page in range(1, 25):
        url = getPageUrl(paperDate, page)
        dirpath = '{prefix:s}{year:04d}/{month:02d}/{day:02d}/'.format(
            prefix=pathPrefix, year=paperDate.year, month=paperDate.month, day=paperDate.day)
        path = getPagePath(paperDate, page, dirpath)
        print("get {url} into {path}".format(url=url, path=path))

        try:
            try:
                os.makedirs(dirpath)
            except OSError:
                pass

            downloadFile(url=url, path=path)
        except Exception as err:
            print("get pdf page file of {} failed. Caused by {}".format(url, err))
            pass
    print("[{ts}]Unite and compress paper pdf {date}".format(
        ts=datetime.now(), date=paperDate.date()))
    unitAndCompress(paperDate=paperDate, pathPrefix=pathPrefix)

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
    parser.add_argument('--path', dest='path',
                        action='store', default='./')
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

    print("[{ts}] Start scrpy pdfs Renmin Ribao from {start} to {end} to {pathPrefix:s} with {process:d} processes.".format(
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

    # while now < end:
    #     now = now + timedelta(days=1)
    #     try:
    #         scrpyPaper(paperDate=now, pathPrefix="/home/ylin/host_home/renminRibao/")
    #     except Exception as err:
    #         print("Get paper {0} failed. Caused by {1}".format(
    #             str(now.date()), err))

    # return


if __name__ == '__main__':
    main()
