import re
import sys
import json
import pymongo
from pymongo import MongoClient
import pandas as pd
import dateutil.parser as dateparser
from datetime import datetime
import datetime as dt
import requests

def getPeriod(date):
    date_compare = datetime.strptime(date, '%m-%d-%Y')
    starting_date = datetime.strptime('1-1-2018', '%m-%d-%Y')
    i=1
    while i <= 13:
        if((date_compare >= starting_date) and (date_compare < (starting_date + dt.timedelta(days=28)))):
            return 'P'+str(i)
        else:
            starting_date = starting_date + dt.timedelta(days=28)
            if (i == 13):
                i=1
            else:
                i+=1


    return 'P13'

def newReviews(reviews):
    print('in newReviews')
    print(len(reviews.index))
    print(reviews)
    client = MongoClient()
    mongodb_uri = 'mongodb://admin:ACP2018@ds145304.mlab.com:45304/reviews';
    client = MongoClient(mongodb_uri)

    db = client.reviews
    reviews_db = db.reviews

    locations=[]
    ratings=[]
    dates=[]
    comments=[]
    platform=[]
    periods=[]
    years=[]

    new_reviews = []
    i=0
    while i < len(reviews.index):
        r = reviews_db.find_one({'Content':reviews.iloc[i].get('Content'),
                                'Location':reviews.iloc[i].get('Location'),
                                'Date':reviews.iloc[i].get('Date'),
                                'Rating':reviews.iloc[i].get('Rating')})
        if (r is not None):
            print('found review')
        else:
            # print('new review')
            new_review = reviews.iloc[i]
            ratings.append(new_review.get('Rating'))
            comments.append(new_review.get('Content'))
            dates.append(new_review.get('Date'))
            locations.append(new_review.get('Location'))
            platform.append(new_review.get('Platform'))
            periods.append(new_review.get('Period'))
            years.append(new_review.get('Year'))

            insert_review = { 'Location': new_review.get('Location'),
                                'Date': new_review.get('Date'),
                                'Rating': new_review.get('Rating'),
                                'Content': new_review.get('Content'),
                                'Platform': new_review.get('Platform'),
                                'Period': new_review.get('Period'),
                                'Year': new_review.get('Year')}
            reviews_db.insert_one(insert_review)
        i += 1

    new_reviews = {
        'Location':locations,
        'Content':comments,
        'Date':dates,
        'Platform':platform,
        'Period':periods,
        'Year':years
    }
    return new_reviews

def googleReviews(accessToken):
    print('in googleReviews accessToken: ')
    print(accessToken)
    access_token=accessToken
    headers = {
    'authorization': "Bearer " + access_token,
    'content-type': "application/json",
    }

    url = 'https://mybusiness.googleapis.com/v4/accounts'
    response = requests.get(url, headers=headers)
    response=response.content.decode("utf-8")
    accounts=json.loads(response)
    account_name=accounts.get('accounts')[0].get('name')

    locations_url='https://mybusiness.googleapis.com/v4/'+account_name+'/locations'
    locations_response=requests.get(locations_url,headers=headers)
    locations_response=locations_response.content.decode("utf-8")
    locations=json.loads(locations_response)

    locations_list=locations.get('locations')
    location_names=[]

    stores=[]
    addresses=[]
    ratings=[]
    dates=[]
    comments=[]
    platform=[]
    periods=[]
    years=[]

    i=0
    while i < len(locations_list):
        location_name=locations_list[i].get('name')
        loc_url='https://mybusiness.googleapis.com/v4/'+location_name
        loc_response=requests.get(loc_url,headers=headers)
        loc_response=loc_response.content.decode("utf-8")
        loc=json.loads(loc_response)
        address=loc.get('address').get('addressLines')
        if (address[0]=='129 South Main St'):
            print('found grapevine main st')
            store_name = 'Grapevine Main St'
        else:
            store_name=loc.get('address').get('locality')

        print (store_name)

        reviews_url='https://mybusiness.googleapis.com/v4/'+location_name+'/reviews'
        reviews_response=requests.get(reviews_url,headers=headers)
        reviews_response=reviews_response.content.decode("utf-8")
        reviews=json.loads(reviews_response)

        if (reviews.get('reviews') is not None):
            j=0
            while (j < len(reviews.get('reviews'))):
                rating=reviews.get('reviews')[j].get('starRating')
                comment=reviews.get('reviews')[j].get('comment')
                if (comment is None):
                    comment=""
                date=dateparser.parse(reviews.get('reviews')[j].get('createTime')).strftime('%m-%d-%Y')
                year=dateparser.parse(reviews.get('reviews')[j].get('createTime')).strftime('%Y')

                today=dt.datetime.today().strftime('%m-%d-%Y')
                # date_compare = datetime.strptime(dateparser.parse(date).strftime('%m-%d-%Y'), '%m-%d-%Y')
                if (date == today):
                    ratings.append(rating)
                    comments.append(comment)
                    dates.append(date)
                    stores.append(store_name)
                    addresses.append(address)
                    platform.append('Google')
                    periods.append(getPeriod(date))
                    years.append(year)
                j+=1
        i+=1
    reviews = pd.DataFrame()
    reviews['Location'] = stores
    reviews['Date'] = dates
    reviews['Rating'] = ratings
    reviews['Content'] = comments
    reviews['Platform'] = platform
    reviews['Period'] = periods
    reviews['Year'] = years

    new_reviews=newReviews(reviews)

    return new_reviews

if  __name__ == '__main__':
    # findProfanity.py executed as script
    googleReviews(sys.argv[1])
