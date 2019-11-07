from gazpacho import get, Soup
import datetime


MonthNumber={'JANUARY':1,'FEBRUARY':2,'MARCH':3,'APRIL':4,'MAY':5,'JUNE':6,'JULY':7,'AUGUST':8,'SEPTEMBER':9,'OCTOBER':10,'NOVEMBER':11,'DECEMBER':12}

URL = "https://en.wikipedia.org/wiki/Taoiseach"
html = get(URL)
soup = Soup(html)
tables = soup.find("table")
president_data = tables[2].find("tr")
presidentRowSpan=0


 
def getDate(day,pyear):
    dayMonth=day.split(' ')
    year=''
    if(pyear.find('<sup id')>0):
        year=pyear[pyear.find('<br />')+6:pyear.find('<sup id')]
    else:
        year=pyear[pyear.find('<br />')+6:pyear.find('\n</td>')]
    return datetime.date(int(year),MonthNumber[dayMonth[1].upper()],int(dayMonth[0]))

def getDOB(wikiurl):
    url='https://en.wikipedia.org'+wikiurl
    print(url)
    return ""

for i,row in enumerate(president_data[2:]):
    partyName=''
    constituency=""
    officeFromDate=""
    officeToDate=""
    DOB=""
    presidentName=""
    r = row.find("td")
    print(i)
    if(i != 9 and row.find("th")):

        if(i==0):
            partyName=president_data[3].find('td')[0].text+','+r[4].text   
        else:
            partyName=r[4].text

        presidentName=r[1].text
        nameLink=str(r[1].find('a')[0])
        DOB=getDOB(nameLink[nameLink.find('<a href="')+9:nameLink.find('" title')])
        span=r[1].find("span")
        
        if(type(span.find("a")) is list):
            for i in span.find("a"):
                constituency+=i.text+','
        else:
            constituency=span.find("a").text

        officeFromDate=str(getDate(str(r[2].text),str(r[2])))
        if(str(r[3]).find('br')>0):
            officeToDate=str(getDate(str(r[3].text),str(r[3])))
        else:
            officeToDate='Incumbent'

        print(presidentName+','+partyName+','+officeFromDate+','+officeToDate+','+constituency)
        print('-------------------------------------------------------------')
    

    

#def dateconvert(dateconvert)
