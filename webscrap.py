from gazpacho import get, Soup
import datetime
from pandas.io.html import read_html
import pandas as pd


MonthNumber={'JANUARY':1,'FEBRUARY':2,'MARCH':3,'APRIL':4,'MAY':5,'JUNE':6,'JULY':7,'AUGUST':8,'SEPTEMBER':9,'OCTOBER':10,'NOVEMBER':11,'DECEMBER':12}

URL = "https://en.wikipedia.org/wiki/Taoiseach"
html = get(URL)
soup = Soup(html)
tables = soup.find("table")
president_data = tables[2].find("tr")



 
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
    dobHtml=get(url)
    dobSoup=Soup(dobHtml)
    dobTable = dobSoup.find("table")[0].find('tr')
    if(dobSoup.find("table")[0].attrs['class'] != "infobox vcard"):
        dobTable = dobSoup.find("table")[1].find('tr')
    for dobRow in dobTable:
        if(not dobRow.find('table') and dobRow.find('th') and dobRow.find('th').text=="Born"):
            if(type(dobRow.find('span')) is list):
                dob=str(dobRow.find('span')[0])
                dob=dob[dob.find('class="bday">')+13:dob.find('</span>)')]
                return dob
            else:
                dob=str(dobRow.find('span'))
                dob=dob[dob.find('class="bday">')+13:dob.find('</span>)')]
                return dob  

def getVicePresident(currentindex,rowspan):
    df=dfVP[currentindex:currentindex+rowspan]
    vpName=''
    dail=''
    for i in (set(df['VicePresident'].tolist())):
        vpName+=i+','
    for i in (set(df['Dail'].tolist())):
        dail+=i+','
    return vpName.rstrip(','),dail.rstrip(',')

def getVPDailDF():
    wikitables = read_html(URL,  attrs={"class":"wikitable"})
    df=wikitables[0]
    df=df.drop(columns=[0,1,2,3,4,5,6,7,8])
    df.columns=['VicePresident','Dail']
    df=df.drop([0,1]) 
    return df


dfVP=getVPDailDF()


for i,row in enumerate(president_data[2:]):
    partyName=''
    constituency=""
    officeFromDate=""
    officeToDate=""
    DOB=""
    presidentName=""
    VicePresident=""
    Dail=""
    r = row.find("td")
    if(i != 9 and row.find("th")):
        rowspan=1
        if(i==0):
            partyName=president_data[3].find('td')[0].text+','+r[4].text   
        else:
            partyName=r[4].text
        
        if(r[1].attrs.get('rowspan')):
            rowspan=int(r[0].attrs['rowspan'])

        VicePresident,Dail=getVicePresident(i,rowspan)
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

        print(presidentName+','+partyName+','+type(officeFromDate)+','+officeToDate+','+constituency+','+type(DOB)+','+VicePresident+','+Dail)
        print('-------------------------------------------------------------')
    


#def dateconvert(dateconvert)
