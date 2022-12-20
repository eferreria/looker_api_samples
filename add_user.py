# Copyright 2022 Google. This software is provided as-is, without warranty or representation for any use or purpose. 
# Your use of it is subject to your agreement with Google. 
#
# This Python Script User Looker SDK to call Looker APIs to perform the following functions:
#		* Reads a CSV file for a Looker User Email, Looker Group Name and Looker User Attribute Value
#		* The CSV import file can be of any name, but must be of the format {email},{group_name},{user_attribute_value}
#		* This script assumes that this will always update the same User Attribute ID (15 for this example)
#		* The program steps thru each record in the CSV and
#				1. Checks if the Group Exists, Creates a new group if not exist
#				2. Checks if User Exists via email, creates a new user if not exist
#				3. Adds User to Group
#				4. Sets User Attribute (User Attribute ID 15 (default)) to User Attribute Value for Group

import json
import sys
from typing import cast, Dict, List, Union
from csv import reader

import looker_sdk
from looker_sdk import models, error, models40

sdk = looker_sdk.init40("../looker_dev.ini")

# takes the filename from the command as an option
file_name = sys.argv[1]

# the user_attribute_id can be found on the URL of the User Attribute in the Looker IDE
user_attribute_id = '15'

# search users by email, returns user_id
def search_users_by_email(email):
	users = sdk.search_users(email=email)
	if len(users) == 0:
		return None 
	else: 
		return users[0]["id"]

# add user_id to group_id, returns     
def add_user_to_group(user_id, group_id):
	results = sdk.add_group_user(group_id=group_id, body=models40.GroupIdForGroupUserInclusion(user_id=user_id))
	print(f"Added User {user_id} to Group {group_id}")
	return results

# sets user_attribute on group_id
def set_user_attribute_on_group(group_id, user_attribute_id, user_attribute_value:str):
	results = sdk.update_user_attribute_group_value(group_id = group_id, user_attribute_id=user_attribute_id, body=models40.UserAttributeGroupValue(
		value=user_attribute_value))
	print(f"Set {user_attribute_id} to {user_attribute_value} for Group ID:{group_id}")
	return results

def set_user_attribute_on_user(user_id, user_attribute_id, user_attribute_value:str):
	results = sdk.set_user_attribute_user_value(user_id=user_id, user_attribute_id=user_attribute_id, body=models40.UserAttributeWithValue(
		value=user_attribute_value))
	print(f"Set {user_attribute_id} to {user_attribute_value} for User ID:{user_id}")

# creates a new user with emaill, returns user_id	
def create_users(email):
  new_user = sdk.create_user(
            body=looker_sdk.models40.WriteUser(
                credentials_email=looker_sdk.models40.WriteCredentialsEmail(
                    email=email,
                    forced_password_reset_at_next_login=False
                ),
                is_disabled=False,
                models_dir_validated=False
            )
        )

  # Create email credentials for the new user
  sdk.create_user_credentials_email(
                user_id=new_user.id,
                body=looker_sdk.models40.WriteCredentialsEmail(
                    email=email,
                    forced_password_reset_at_next_login=False
                ))
  return new_user.id
               

# MAIN Program Step
# Open CSV file
with open(file_name, 'r') as read_obj:
	csv_reader = reader(read_obj)
	
	# for each record in the CSV file
	for row in csv_reader:
		user_email = row[0]
		group_name = row[1]
		user_attribute_value = row[2]
		group_yn = row[3]
		print(f"{user_email}, {group_name}, {user_attribute_value}")
		
		# search if group exists, if logic to create a new group if not exist
		group = sdk.search_groups(name=group_name, fields="id")
		if group:
			group = group[0]
			group_id = group.id
			print(f"Group ID is {group.id}")
		else:
			result = sdk.create_group(body=models40.WriteGroup(name=group_name), fields="id")
			group_id = result.id
			print(f"Created {group_name} with id {group_id}")
		
		# search if user exists, if logic to create a new user if not exist
		user_id = search_users_by_email(user_email)
		if user_id is not None:
			print(f"User ID {user_id} with email {user_email} exists")
		else:
			user_id = create_users(user_email)
			print(f"{user_email} has been created with id {user_id}")
		
		# group and user exists, add user to group
		add_user_to_group(user_id, group_id)
		
		# set attribute on group if group_yn = 1, else set on user
		# overrides existing value
		if group_yn == '1':
			set_user_attribute_on_group(group_id, user_attribute_id, user_attribute_value)
		else:
			set_user_attribute_on_user(user_id, user_attribute_id, user_attribute_value)
	# end for loop, close CSV file
	

