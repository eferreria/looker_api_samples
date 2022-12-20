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
import subprocess
from typing import cast, Dict, List, Union

import looker_sdk
from looker_sdk import models, error

# Program Flow
# 1. Look for User ID
# 2. Delete Scheduled Email
#     - get all scheduled plans (user id)
        # - delete scheduled plan
# 3. Move Content to Archive
        # - export user folder
        # - import user folder to archive folder
# 4. Delete User

sdk = looker_sdk.init40("../looker_dev.ini")
email = sys.argv[1]
host = sys.argv[2]
ldeploy_env = 'Eric_Looker'
ldeploy_ini = '../looker_dev.ini'

# search users by email, returns user_id
def search_users_by_email(email):
	users = sdk.search_users(email=email)
	if len(users) == 0:
		return None 
	else: 
		return users[0]["id"]

def get_scheduled_plans_by_userid(user_id):
    scheduled_plans = sdk.all_scheduled_plans(user_id=user_id,fields="id")
    if len(scheduled_plans) == 0:
        return None 
    else: 
        return scheduled_plans

def delete_scheduled_plan_by_id(scheduled_plan_id):
    response = sdk.delete_scheduled_plan(scheduled_plan_id=scheduled_plan_id)

def search_user_folder_to_export(user_id):
    target_folder = sdk.search_folders( parent_id='2', creator_id=user_id)
    if len(target_folder) == 0:
        return None
    else:
        return target_folder[0]["id"]

user_id = search_users_by_email(email)
plans = get_scheduled_plans_by_userid(user_id)
for i in range(len(plans)):
    plan_id = plans[i]["id"]
    # delete_scheduled_plan_by_id(scheduled_plan_id=plan_id)
    print(f'Found {plan_id} for {email}')

user_folder = search_user_folder_to_export(user_id)

subprocess_command = 'ldeploy content export --env '+ ldeploy_env +' --ini ' + ldeploy_ini + ' --folders '+ user_folder +' --local-target exported_folder'
subprocess.call([subprocess_command], shell=True)

user_folder = "'./exported_folder/Users'"
subprocess_command = 'ldeploy content import --env '+ ldeploy_env +' --ini '+ ldeploy_ini +'  --folders '+ user_folder +' --recursive --target-folder Shared/Archives/'+ email
subprocess.call([subprocess_command], shell=True)
