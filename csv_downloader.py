from datetime import datetime
import urllib2

symbol = 'PEP'
day = '1'
url = 'http://www.google.com/finance/getprices?i=60&p=' + day + 'd&f=d,o,h,l,c,v&df=cpct&q=' + symbol
res = urllib2.urlopen(url)
content = res.read()

filename = datetime.now().strftime('%y-%m-%d-') + symbol + '-' + day

with open(filename, 'w') as f:
    f.write(content)
