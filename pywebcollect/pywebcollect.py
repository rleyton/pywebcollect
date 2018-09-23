#!/usr/bin/env/ python
################################################################################
#    Copyright (c) 2018 Richard Leyton
#    This file is part of pywebcollect.
#    
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"), 
#    to deal in the Software without restriction, including without limitation 
#    the rights to use, copy, modify, merge, publish, distribute, sublicense, 
#    and/or sell copies of the Software, and to permit persons to whom the 
#    Software is furnished to do so, subject to the following conditions:
#    
#    The above copyright notice and this permission notice shall be included in 
#    all copies or substantial portions of the Software.
################################################################################

import urllib
import urllib.request
import json
import datetime

class WebCollect(object):
    # datetime presumes midnight, so a calculation run during the day, on the day of expiration, needs to be at least 1
    DEFAULT_EXPIRATION_WINDOW=1
    EXPIRATION_WINDOW=DEFAULT_EXPIRATION_WINDOW
    BASE_URL='https://webcollect.org.uk/api/v1'
    today=datetime.datetime.today()

    def __init__(self,account=None,token=None):
        self.baseURL="/".join((self.BASE_URL,account))
        self.token=token


    # Main entry point to call a WebCollect API endpoints
    # No formal documentation, but PHP example lists:
    # /member - fetch members;
    #            optional parameters:
    #               email=EMAIL
    #               unique_id=ID
    #               webcollect_id=ID
    # /event - fetch events;
    #           optional parameters:
    #               short_name=NAME
    #               start_date=DATE
    #               end_date=DATE
    def call(self,method,params,expiration=None):

        url=self.baseURL

        if method is not None:
            url+=method

        if params is not None:
            url+="?"+urllib.parse.urlencode(params)

        if expiration is not None:
            self.EXPIRATION_WINDOW=expiration

        headers = {'Authorization':"Bearer "+self.token}
        req=urllib.request.Request(url,None,headers)

        with urllib.request.urlopen(req) as response:
            result=response.read()

        # store the complete result
        self.full_result=json.loads(result.decode('utf-8'))
        self._parseresult()

    # Fetch the 'current' subscription a member has. With monthly options, there may be a few of these, so just pick the first
    # membership providing subscription, and return that.
    def _getCurrentSubscription(self,member={}):
        # for all of the subscriptions a member has
        for subscription in member['subscriptions']:
            if subscription['provides_membership'] is True:
                start=datetime.datetime.strptime(subscription['start_date'],'%Y-%m-%d')
                end=datetime.datetime.strptime(subscription['end_date'],'%Y-%m-%d')+ datetime.timedelta(days=self.EXPIRATION_WINDOW)
                # is it an active subscription?
                if ( start < self.today ) and (self.today <= end):
                    # keep the flagged subscription marked
                    member['PY_ACTIVESUB']=subscription
                    return subscription
                else:
                    True

        return None

    # parse internal results (make iteratable?)
    def _parseresult(self,keepExpiredSubscriptions=False):
        self.memberLookup={}

        # Iterate over results
        for member in self.full_result:
            # useful conversion
            if member['dob'] is not None:
                member['PYDOB']=datetime.datetime.strptime(member['dob'],'%d-%m-%Y')

            # do we want All The Members Ever
            if keepExpiredSubscriptions==True:
                self.memberLookup[member['email']]=member
            else:
                # We are filtering out members without an active subscription
                currentSub=self._getCurrentSubscription(member)
                if currentSub is not None:
                    self.memberLookup[member['email']]=member

    def subscriptions(self):
        return self.memberLookup

    def JSONSubscriptions(self):
        return self.full_result

    def ageCategory(self,member):
        if member is not None:
            if 'PYDOB' in member:
                member['PYAGE']=self.today.year - member['PYDOB'].year - ((self.today.month, self.today.day) < (member['PYDOB'].month, member['PYDOB'].day))
                if member['form_data']['Gender']=='Female':
                    member['PYGENDER']='W'
                else:
                    member['PYGENDER']='M'
                if member['PYAGE'] < 35:
                    return('S'+member['PYGENDER'])
                else:
                    if 35 <= member['PYAGE'] <= 39:
                        cat='35'
                    elif 40 <= member['PYAGE'] <= 44:
                        cat='40'
                    elif 45 <= member['PYAGE'] <= 49:
                        cat='45'
                    elif 50 <= member['PYAGE'] <= 54:
                        cat='50'
                    elif 55 <= member['PYAGE'] <= 59:
                        cat='55'
                    else:
                        cat='60+'
                return('V'+member['PYGENDER']+cat)