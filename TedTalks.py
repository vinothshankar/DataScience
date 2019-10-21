cd cdimport mysql.connector
import ast
import pandas as pd
import sqlalchemy as sqlorm
import operator
import matplotlib.pyplot as plt
import itertools 
import datetime as dt

def dbConnection():
    mysql.connector.connect(user='root', password='root',host='127.0.0.1',database='tedtalks')
    db_connection_str = 'mysql+pymysql://root:root@127.0.0.1/tedtalks'
    return sqlorm.create_engine(db_connection_str)

def getAll(db_conn):
    return pd.read_sql("SELECT * FROM `tedtalks`.`ted_main`", con=db_conn)

def getTags():
    tag_list = tedmain['TAGS'].tolist()
    tags=set()
    for i in tag_list:
        tags=tags.union(set(ast.literal_eval(i)))
    return tags

def getTagsCount(tedmain):
    tags_count={}
    for i in getTags():
        tags_count[i]=sum(tedmain['TAGS'].str.contains(i))
    return dict( sorted(tags_count.items(), key=operator.itemgetter(1),reverse=True))

def showTopFiveTags():
    data=getTagsCount(tedmain)
    tags_top_5=dict(itertools.islice(data.items(), 5)) 
    plt.bar(range(len(tags_top_5)), list(tags_top_5.values()), align='center')
    plt.xticks(range(len(tags_top_5)), list(tags_top_5.keys()))
    plt.show()

def showLastFiveTags():
    data=getTagsCount(tedmain)
    tags_last_5= dict(list(data.items())[len(data)-5: len(data)])
    plt.bar(range(len(tags_last_5)), list(tags_last_5.values()), align='center')
    plt.xticks(range(len(tags_last_5)), list(tags_last_5.keys()))
    plt.show()

def showVideosByYear():
    plt.bar(range(len(publishedYearsCounts)), list(publishedYearsCounts.values()), align='center')
    plt.xticks(range(len(publishedYearsCounts)), list(publishedYearsCounts.keys()))
    plt.show()

def showVideosByMonth():
    plt.bar(range(len(publishedMonthsCounts)), list(publishedMonthsCounts.values()), align='center')
    plt.xticks(range(len(publishedMonthsCounts)), list(publishedMonthsCounts.keys()))
    plt.show()

def showTopDiscussions():
    commentsCountByTags=getTopDiscussionTagsByCount()
    commentsTopFive=dict(itertools.islice(commentsCountByTags.items(), 5)) 
    plt.bar(range(len(commentsTopFive)), list(commentsTopFive.values()), align='center')
    plt.xticks(range(len(commentsTopFive)), list(commentsTopFive.keys()))
    plt.show()

def showTopViewsByTags():
    viewsCountByTags=getTopViewsByTags()
    viewsTopFive=dict(itertools.islice(viewsCountByTags.items(), 5)) 
    plt.bar(range(len(viewsTopFive)), list(viewsTopFive.values()), align='center')
    plt.xticks(range(len(viewsTopFive)), list(viewsTopFive.keys()))
    plt.show()

def getPublishedYearsMonths(tedmain):
    publishedYears=[]
    publishedMonths=[]
    publishedYearsCounts={}
    publishedMonthsCounts={}
    for i in tedmain["PUBLISHED_DATE"].tolist():
        publishedYears.append(dt.datetime.fromtimestamp(i).date().year)
        publishedMonths.append(dt.datetime.fromtimestamp(i).date().strftime("%B"))
    for i in publishedYears:
        publishedYearsCounts[i]=publishedYearsCounts.get(i,0)+1
    for i in publishedMonths:
        publishedMonthsCounts[i]=publishedMonthsCounts.get(i,0)+1
    return [publishedYearsCounts,publishedMonthsCounts]

def getTopDiscussionTagsByCount():
    tags=getTags()
    commentsCountByTags={}
    for i in tags:
        j=tedmain.loc[tedmain['TAGS'].str.contains(i),['COMMENTS']]
        commentsCountByTags[i]=sum(j['COMMENTS'])
    return dict(sorted(commentsCountByTags.items(), key=operator.itemgetter(1),reverse=True))

def getTopViewsByTags():
    tags=getTags()
    viewsCountByTags={}
    for i in tags:
        j=tedmain.loc[tedmain['TAGS'].str.contains(i),['VIEWS']]
        viewsCountByTags[i]=sum(j['VIEWS'])
    return dict(sorted(viewsCountByTags.items(), key=operator.itemgetter(1),reverse=True))




db_connection = dbConnection()
tedmain = getAll(db_connection)
publishedYearsCounts,publishedMonthsCounts=getPublishedYearsMonths(tedmain)

