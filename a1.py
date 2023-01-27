#!/usr/bin/env python3

import configparser
import os 
import sys 
import pathlib
import boto3
import readline

from botocore.exceptions import ClientError
from command_functionality import *

# TODO:
    # - When you pass commands[1], make sure there is actually a second command given OR just pass commands and create helper function to detect if only 1 things was passed

# AWS access key id and secret access key information found in configuration file (S5-S3.conf)
config = configparser.ConfigParser()
config.read("S5-S3.conf")
aws_access_key_id = config['default']['aws_access_key_id']
aws_secret_access_key = config['default']['aws_secret_access_key']

try:

    # Establish an AWS session
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # Set up client and resources
    s3 = session.client('s3')
    s3_res = session.resource('s3')

    print ( "Welcome to the S3 Storage Shell (S5)" )
    cwd = ""
    
    # TODO: Test the following loop:
    # Prompt loop - if no buckets exist in S3 space
    # response = s3.list_buckets()
    # if not (response['Buckets']):
    #     current_command = input("S5> ")
    #     # response = s3.list_buckets()
    #     while(not response['Buckets'] and (current_command != 'quit' and current_command != 'exit')):
    #         print("here")
    #         commands = current_command.split()
            
    #         if(commands[0] != "create_bucket"):
    #             print("S3 storage space is empty. Please create a bucket using the command 'create_bucket /<bucket_name>'")
    #         else:
    #             if(check_name(bucket_name)):
    #                 create_bucket(s3, bucket_name)
    #         response = s3.list_buckets()
    #         current_command = input("S5> ")

    # Prompt loop
    current_command = input("S5> ")
    while(current_command != 'quit' and current_command != 'exit'):
        commands = current_command.split()

        # When user is at root
        if(cwd == ""):
            if(commands[0] == "cwlocn"):
                print("/")
            elif(commands[0] == "chlocn"):
                if(len(commands) == 2 and (commands[1] == "/" or commands[1] == "~")):
                    cwd = ""
                elif(commands[1] == ".." or commands[1] == "../.."):
                    print("Cannot change directory: user is at root")
                else:
                    if(check_location(s3, s3_res, cwd, commands)):
                        if(is_relative_path(commands[1])):
                            cwd = build_cwd(cwd, commands)
                        else:
                            cwd = commands[1]
            elif(commands[0] == "list"):
                if(count_buckets(s3) == 0): # TODO: test this
                    print("No buckets exits in your S3 space. Please create a bucket using 'create_bucket'")
                else:
                    list_bdo(s3, s3_res, cwd, commands)
            elif(commands[0] == "create_bucket"):
                create_bucket(s3, s3_res, commands)
            elif(commands[0] == "delete_bucket"):
                delete_bucket(s3, s3_res, cwd, commands)
            else:
                print("Please chlocn to a location in S3 space\nAvailable commands at root:\n   cwlocn: current working location\n   chlocn: change location\n   list: lists existing buckets\n   create_bucket: creates new bucket\n   delete_bucket: deletes a given bucket")
        
        # When user is in a bucket/directory
        else:
            if(commands[0] == "locs3cp"):
                copy_local_to_cloud(s3, s3_res, cwd, commands)
            elif(commands[0] == "s3loccp"):
                copy_cloud_to_local(s3, s3_res, cwd, commands)
            elif(commands[0] == "create_bucket"):
                create_bucket(s3, s3_res, commands)
            elif(commands[0] == "create_folder"):
                create_folder(s3, s3_res, cwd, commands)
            elif(commands[0] == "chlocn"):
                if(len(commands) == 2 and (commands[1] == "/" or commands[1] == "~")):
                    cwd = ""
                elif(commands[1] == ".."):
                    full_path_split = cwd.split('/')
                    cwd = cwd.replace("/"+full_path_split[-1], '')
                elif(commands[1] == "../.."):
                    full_path_split = cwd.split('/')
                    cwd = cwd.replace("/"+full_path_split[-2]+"/"+full_path_split[-1], '')
                else:
                    if(check_location(s3, s3_res, cwd, commands)):
                        if(is_relative_path(commands[1])):
                            cwd = build_cwd(cwd, commands)
                        else:
                            cwd = commands[1]
            elif(commands[0] == "cwlocn"):
                get_cwd(cwd)
            elif(commands[0] == "list"): # TODO: -l flag
                list_bdo(s3, s3_res, cwd, commands)
            elif(commands[0] == "s3delete"):
                delete_obj(s3, s3_res, cwd, commands)
            elif(commands[0] == "delete_bucket"):
                delete_bucket(s3, s3_res, cwd, commands)
            else:
                non_cloud_cmd(current_command)
        # print("current working directory: " + cwd)
        current_command = input("S5> ")

except ClientError as e:
    if e.response['Error']['Code'] == 'EntityAlreadyExists':
        print("User already exists")
    else:
        print("Unexpected error: %s" % e)
# except:
#     print ( "You could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3" )
