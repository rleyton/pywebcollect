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

import csv
import pywebcollect
import json

# YOU NEED TO CHANGE THE PARAMETERS HERE TO YOUR OWN
# account is your webcollect account id
# token is a valid token from 'Manage API tokens': https://webcollect.org.uk/orgadm/index.php?page=api_token
example=pywebcollect.WebCollect(account='webcollectaccount',token='YOURAPITOKENFROMWEBCOLLECT')

# Now call it to fetch a single email address (your own?)
example.call(method="/member",params={'email':'YOUR@EMAIL.ADDRESS})

# Dump it out
print("JSON: "+json.dumps(example.JSONSubscriptions(),indent=4,default=str))

# Now call it with no paramters to fetch ALL MEMBERS
example.call(method="/member",params=None)

# Dump out the raw data (verbose!)
print("JSON: "+json.dumps(example.JSONSubscriptions(),indent=4,default=str))


# So, more usefully, we want a CSV listing member's name, date of birth, and their Scottish Athletics membership number.
# This is captured in a form field called SA_number.
#
# This example iterates over the result of all (active) memberships, which are produced by subscriptions() method,
# and generates a CSV and some summary stdout info

with open('members.csv','w') as csv_file:
    membersCSV=csv.writer(csv_file)
    count = 0
    for email, activeMember in sorted(example.subscriptions().items()):
        count += 1
        saNumber=activeMember['form_data']['SA_number']
        if saNumber is None or saNumber==0:
            saNumber='N/A'
        else:
            saNumber='SA'+str(saNumber)

        print("%4s: %s %s %s %s SA%s %s" % ( count, email, activeMember['firstname'].title(), activeMember['lastname'].title(), activeMember['dob'],saNumber, example.ageCategory(activeMember)))

        membersCSV.writerow([count,activeMember['firstname'].title(),activeMember['lastname'].title(),email,activeMember['dob'],activeMember['PYAGE'],saNumber])

