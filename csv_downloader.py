from datetime import datetime
import urllib2

def csv_from_google(symbol, day=10):
    day = str(day)
    url = 'http://www.google.com/finance/getprices?i=60&p=' + day + 'd&f=d,o,h,l,c,v&df=cpct&q=' + symbol
    res = urllib2.urlopen(url)
    content = res.read()

    filename = symbol + datetime.now().strftime('-%y-%m-%d') + '-' + day

    with open(filename, 'w') as f:
        f.write(content)
