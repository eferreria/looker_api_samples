# Copyright 2022 Google. 
# This software is provided as-is, without warranty or representation for any use or purpose. 
# Your use of it is subject to your agreement with Google. 
#
# Looker API Calls Used
# search_users (https://developers.looker.com/api/explorer/4.0/methods/User/search_users?sdk=ts&s=search+user)
# all_user_sessions (https://developers.looker.com/api/explorer/4.0/methods/User/all_user_sessions?sdk=ts&s=session)
# delete_user_sessions (https://developers.looker.com/api/explorer/4.0/methods/User/delete_user_session?sdk=ts&s=session)

import json
import sys
from typing import cast, Dict, List, Union

import looker_sdk
from looker_sdk import models, error

# Program Flow
# Inputs - User Email
# Steps
# 1 - Find User ID using Email
# 2 - Find Sessions for User ID
# 3 - Kill sessions for User ID

sdk = looker_sdk.init40("../looker_dev.ini")

email = sys.argv[1]

# search users by email, returns user_id
def search_users_by_email(email):
	users = sdk.search_users(email=email)
	if len(users) == 0:
		return None 
	else: 
		return users[0]["id"]

# search sessions by id, returns session id
# A user can have multiple sessions if the Concurrent Sessions are Enabled
def search_user_sessions_by_id(user_id):
    sessions = sdk.all_user_sessions(user_id=user_id)
    if len(sessions) == 0:
        return None
    else:
        return sessions

# kill a user session
def delete_session_by_session_id(session_id):
    status = sdk.delete_user_session(
        user_id=user_id,
        session_id=session_id
    )

user_id = search_users_by_email(email)
sessions = search_user_sessions_by_id(user_id)
print(f'User email {email} has id {user_id}')

# iterate thru all the sessions
for i in range(len(sessions)):
    session_id = sessions[i]["id"]
    delete_session_by_session_id(session_id)
    print(f'Deleted {session_id} for {email} with id {user_id}')
