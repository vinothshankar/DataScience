from gazpacho import get, Soup
import datetime
from pandas.io.html import read_html
import pandas as pd
import mysql.connector


MonthNumber={'JANUARY':1,'FEBRUARY':2,'MARCH':3,'APRIL':4,'MAY':5,'JUNE':6,'JULY':7,'AUGUST':8,'SEPTEMBER':9,'OCTOBER':10,'NOVEMBER':11,'DECEMBER':12}
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="webscrap"
)
URL = "https://en.wikipedia.org/wiki/Taoiseach"
html = get(URL)
soup = Soup(html)
tables = soup.find("table")
president_data = tables[2].find("tr")
Taoiseach=[]

 
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

def mainMethod():
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
            DOB=getDOB(r[1].find('a')[0].attrs['href'])
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

            Taoiseach.append((presidentName,DOB,constituency.rstrip(','),officeFromDate,officeToDate,partyName,VicePresident,Dail))

def insertTaoiseach():
    mycursor = mydb.cursor()
    sql = "INSERT INTO taoiseach (presidentname,dob,constituency,officefrom,officeto,partyname,vicepresident,dail) VALUES (%s, %s,%s,%s,%s,%s,%s,%s)"
    mycursor.executemany(sql, Taoiseach)
    mydb.commit()
    print(mycursor.rowcount, "was inserted.")

def listConstituency():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT distinct(constituency) FROM taoiseach")
    constitutencyList=mycursor.fetchall()
    constitutency=set()
    for row in constitutencyList:
        for c in row[0].split(','):
            constitutency.add(c)
    print(constitutency)

def questionC():
    mycursor = mydb.cursor()
    mycursor.execute("select id,presidentname,vicepresident from taoiseach")
    table=mycursor.fetchall()
    vp=[]
    for i,row in enumerate(table):
        if(i <= len(table)-2):
            if(table[i+1][1] in row[2]):
                vp.append(table[i+1][1])
    print(vp)
    

def questionC():
    mycursor = mydb.cursor()
    mycursor.execute("select id,presidentname,vicepresident from taoiseach")
    table=mycursor.fetchall()
    vp=[]
    presdent=[]
    for i,row in enumerate(table):
        vp.append(row[2])
        presdent.append(row[1])
    for i in presdent:
        if(i in str(vp)):
            print(i)
    

def dateDiff(startdate,todate):
    datetimeFormat = '%Y-%m-%d'
    diff = datetime.datetime.strptime(todate, datetimeFormat)-datetime.datetime.strptime(startdate, datetimeFormat)
    return diff.days

def questionD():
    mycursor = mydb.cursor()
    mycursor.execute("select id,officefrom,officeto,partyname from taoiseach")
    table=mycursor.fetchall()
    ddict={}
    for i,row in enumerate(table):
        if(i!=len(table)-1):
            if(row[3] not in ddict.keys()):
                ddict[row[3]]=dateDiff(str(row[1]),row[2])
            else:
                ddict[row[3]]+=dateDiff(str(row[1]),row[2])
        else:
            ddict[row[3]]+=dateDiff(str(row[1]),str(datetime.date.today()))
    pdays=0
    years=0
    months=0
    days=0
    party=''
    for r in ddict:
        if(ddict[r]>pdays):
            pdays=ddict[r]
            years=int(ddict[r]/365)
            months=int(ddict[r] % 365 /30)
            days=ddict[r]%365%30
            party=r
    print(party+' held the Taoiseach office for longest amount of time for approximately '+str(years)+' years '+str(months)+' months and '+str(days)+ ' days') 

        
def questionE():
    ppartyname=''
    days=0
    mycursor = mydb.cursor()
    mycursor.execute("select id,officefrom,officeto,presidentname from taoiseach")
    table=mycursor.fetchall()
    ddict={}
    for i,row in enumerate(table):
        if(i==0):
            days=dateDiff(str(row[1]),row[2])
            ppartyname=row[3]
        elif(i==len(table)-1):
            if(ppartyname==row[3]):
                days=dateDiff(str(row[1]),str(datetime.date.today()))
                ddict[row[3]]+=days
            else:
                days=dateDiff(str(row[1]),str(datetime.date.today()))
                ppartyname=row[3]
                ddict[row[3]]=days   
        else:
            if(ppartyname==row[3]):
                days+=dateDiff(str(row[1]),row[2])  
            else:
                if(ppartyname not in ddict.keys() or days>ddict[ppartyname]):
                    ddict[ppartyname]=days

                days=dateDiff(str(row[1]),row[2])
                ppartyname=row[3]
    fdays=0                
    years=0
    months=0
    days=0
    party=''
    for j in ddict:
        if(fdays<ddict[j]):
            party=j
            fdays=ddict[j]
            years=int(ddict[j]/365)
            months=int(ddict[j]%365/30)
            days=ddict[j]%365%30

    print(party+' held the office of Taoiseach for longest amount uninterrupted time approximately '+str(years)+' years '+str(months)+' months '+str(days)+' days.')



def questionF():
    ppartyname=''
    days=0
    mycursor = mydb.cursor()
    mycursor.execute("select id,officefrom,officeto,presidentname from taoiseach")
    table=mycursor.fetchall()
    ddict={}
    for i,row in enumerate(table):
        if(i==0):
            days=dateDiff(str(row[1]),row[2])
            ppartyname=row[3]
        elif(i==len(table)-1):
            if(ppartyname==row[3]):
                days=dateDiff(str(row[1]),str(datetime.date.today()))
                ddict[row[3]]+=days
            else:
                days=dateDiff(str(row[1]),str(datetime.date.today()))
                ppartyname=row[3]
                ddict[row[3]]=days   
        else:
            if(ppartyname==row[3]):
                days+=dateDiff(str(row[1]),row[2])  
            else:
                if(ppartyname not in ddict.keys() or days<ddict[ppartyname]):
                    ddict[ppartyname]=days

                days=dateDiff(str(row[1]),row[2])
                ppartyname=row[3]             
    politician=min(ddict.keys(), key=(lambda k: ddict[k])) 
    print(politician+' held the office of Taoiseach for shortest amount of time '+str(ddict[politician])+' days.')

def questionG():
    mycursor = mydb.cursor()
    mycursor.execute("select dail,partyname from taoiseach")
    dailList=mycursor.fetchall()
    dail={}
    for row in dailList:
        for c in row[0].split(','):
            if row[1] in dail.keys():
                dail[row[1]]+=1
            else:
                dail[row[1]]=1
    party=max(dail.keys(), key=(lambda k: dail[k])) 
    print(party+' has held the office of Taoiseach for the largest number of Dáils of '+str(dail[party])+' times')

def questionH():
    mycursor = mydb.cursor()
    mycursor.execute("select dail,presidentname from taoiseach")
    dailList=mycursor.fetchall()
    dail={}
    for row in dailList:
        for c in row[0].split(','):
            if row[1] in dail.keys():
                dail[row[1]]+=1
            else:
                dail[row[1]]=1
    party=max(dail.keys(), key=(lambda k: dail[k])) 
    print(party+' has held the office of Taoiseach for the largest number of Dáils of '+str(dail[party])+' times')
    
    





dfVP=getVPDailDF()  
#mainMethod()
#insertTaoiseach()
#listConstituency()
#questionC()
#questionD()
#questionE()
#questionF()
#questionG()
questionH()

#def dateconvert(dateconvert)
