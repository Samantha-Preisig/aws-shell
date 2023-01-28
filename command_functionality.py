import configparser
import os 
import sys 
import pathlib
import boto3
import re # for regex parsing

def missing_arg(cmd, num_args_needed):
    if(len(cmd) < num_args_needed):
        return True
    return False

def is_file(split_path):
    if(len(split_path[-1].split('.')) != 1): # the last item of split_path contains a '.' for file extension
        return True
    return False

def is_relative_path(path):
    if(len(path.split('/')) > 1 and path.split('/')[0] == ""):
        return False
    return True

# [Local File Functions]
# 3a) Non-cloud related commands
# Assumptions:
# Limitations:
# TODO: Needs formatting

def non_cloud_cmd(cmd):
    returned_value = os.system(cmd)  # returns the exit code in unix
    print(returned_value)

# [Local File Functions]
# 3b) Copy local file to cloud location
# Assumptions:
    # - [Similar to copy_cloud_to_local()] The local file path is relative. The 'root' is the current folder holding all assignment files
    # Eg. A folder 'notes' is created inside this current folder with a file in it 'test.txt'. To copy test.txt into
    # a cloud location, use the following command:
    # S5> locs3cp notes/test.txt /<bucket name>/<full pathname of S3 object>
# Limitations:
# TODO:

def same_file_ext(local, cloud):
    if(local.split('.')[-1] == cloud.split('.')[-1]):
        return True
    return False

def copy_local_to_cloud(s3, s3_res, cwd, cmd):
    if(missing_arg(cmd, 3)):
        print("Usage: locs3cp <full/relative pathname of local file> /<bucket name>/<full pathname of S3 object>")
        return
    
    cloud_path = ""
    if(is_relative_path(cmd[2])):
        cloud_path = cwd+"/"+cmd[2]
    else:
        cloud_path = cmd[2]
    
    bucket_name = cloud_path.split("/")[1]
    if(not bucket_exists(s3_res, bucket_name)):
        print("Unsuccessful copy: bucket does not exist")
        return

    local_path = cmd[1]
    local_path = local_path.split("/")[-1]
    cloud_path = cloud_path.replace("/"+bucket_name+"/", '')

    if(len(local_path.split('.')) == 2 and len(cloud_path.split('.')) == 2 and same_file_ext(local_path, cloud_path)):
        s3.upload_file(local_path, bucket_name, cloud_path)
    else:
        print("Unsuccessful copy")

# [Local File Functions]
# 3c) Copy cloud object to local
# Assumptions:
    # - Files have to be of the same type (ex. copy cloud text file to local text file)
    # - [Similar to copy_local_to_cloud()] The local file path is relative. The 'root' is the current folder holding all assignment files
    # Eg. The following copies 'test.txt' (cloud file) into current local folder with the name 'testing.txt'
    # S5> s3loccp /<bucket name>/<full pathname of S3 object> testing.txt
# Limitations: Cloud file is saved in current local directory (cannot specify local directory)
# TODO: Check if file in cloud exists

def copy_cloud_to_local(s3, s3_res, cwd, cmd):
    if(missing_arg(cmd, 3)):
        print("Usage: s3loccp /<bucket name>/<full pathname of S3 file> /<full/relative pathname of local file>")
        return
    
    cloud_path = ""
    if(is_relative_path(cmd[1])):
        cloud_path = cwd+"/"+cmd[1]
    else:
        cloud_path = cmd[1]
    
    bucket_name = cloud_path.split('/')[1]
    if(not bucket_exists(s3_res, bucket_name)):
        print("Unsuccessful copy: bucket does not exist")
        return

    local_path = cmd[2]
    local_path = local_path.split('/')[-1]
    cloud_path = cloud_path.replace("/"+bucket_name+"/", '')
    if(len(local_path.split('.')) == 2 and len(cloud_path.split('.')) == 2 and same_file_ext(local_path, cloud_path)):
        s3.download_file(bucket_name, cloud_path, local_path)
    else:
        print("Unsuccessful copy")

# [Cloud Functions]
# 4a) Create bucket
# Error handling based on: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
# Assumptions:
# Limitations to check_name():
    # - [TODO] Bucket names must not be formatted as an IP address (for example, 192.168.5.4).
    # - Bucket names must be unique across all AWS accounts in all the AWS Regions within a partition.
    #   A partition is a grouping of Regions. AWS currently has three partitions: aws (Standard Regions),
    #   aws-cn (China Regions), and aws-us-gov (AWS GovCloud (US)).
    # - A bucket name cannot be used by another AWS account in the same partition until the bucket is deleted.
    # - Buckets used with Amazon S3 Transfer Acceleration can't have dots (.) in their names.
# Limitations to create_bucket():
    # - Not the same settings as first bucket I created
# TODO: buckets created don't have the same settings as first bucket created (is this necessary?)

def bucket_exists(s3_res, bucket_name):
    bucket = s3_res.Bucket(bucket_name)
    if not bucket.creation_date:
        return False
    return True

def check_name(name):
    if(len(name) < 3 or len(name) > 63):
        print("Bucket names must be between 3 (min) and 63 (max) characters long")
        return False
    if(name.startswith('xn--')):
        print("Bucket names must not start with the prefix 'xn--'")
        return False
    if(name.endswith('-s3alias')):
        print("Bucket names must not end with the suffix '-s3alias'")
        return False

    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    if(regex.search(name) != None):
        print("Bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-)")
        return False
    if not (name.islower()):
        print("Bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-)")
        return False

    name_arr = list(name)
    if not ((name_arr[0].isnumeric() or name_arr[0].islower()) and (name_arr[-1].isnumeric() or name_arr[-1].islower())):
        print("Bucket names must begin and end with a letter or number")
        return False
    for i in range(0, len(name_arr)):
        if(name_arr[i] == '.' and (name_arr[i+1] == '.')):
            print("Bucket names must not contain two adjacent periods")
            return False
    
    return True

def create_bucket(s3, s3_res, cmd):
    if(missing_arg(cmd, 2)):
        print("Usage: create_bucket /<bucket name>")
        return
    if(is_relative_path(cmd[1])):
        print("Usage: create_bucket /<bucket name>")
        return
    # if(len(cmd[1].split('/')) != 2):
    #     print("Usage: create_bucket /<bucket name>")
    #     return

    bucket_name = cmd[1].replace('/', '')

    if(bucket_exists(s3_res, bucket_name)):
        print("Cannot create an existing bucket")
        return
    
    if(check_name(bucket_name)):
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ca-central-1'})

# [Cloud Functions]
# 4b) Create directory/folder
# Assumptions:
# Limitations: If relative path is given, it is assumed the full path of new directory doesn't exist
# TODO:

def create_folder(s3, s3_res, cwd, cmd):
    if(missing_arg(cmd, 2)):
        print("Usage: create_folder /<full/relative pathname of new folder>")
        return
    
    if(is_relative_path(cmd[1])):
        # if(directory_exists(s3, s3_res, cmd[1])): # directory_exists() doesn't work with relative paths yet
        #     print("Cannot create folder: the directory already exists")
        #     return

        bucket_name = cwd.split('/')[1]
        folder = cmd[1] + "/"
        s3.put_object(Bucket=bucket_name, Key=folder)
    else:
    
        path = ''.join(cmd[1].split('/', 1))
        path_split = path.split('/')
        
        if(len(path_split) == 1): # Only bucket was listed
            print("Cannot create folder: a bucket was given")
            return

        # Creating a folder in a bucket that doesn't exist
        bucket_name = path_split[0]
        if(not bucket_exists(s3_res, bucket_name)):
            print("Cannot create folder: the bucket doesn't exist")
            return
        
        if(directory_exists(s3, s3_res, cmd[1])):
            print("Cannot create folder: the directory already exists")
            return
        
        folder_name = path.replace(bucket_name+"/", '') + "/"
        print(folder_name)
        s3.put_object(Bucket=bucket_name, Key=folder_name)

# [Cloud Functions]
# 4c) Change directory
# Assumptions:
# Limitations:
# TODO: BROKEN -> directory "doesn't exist"

def build_cwd(cwd, cmd):
    # Build full path from relative path
    return cwd+"/"+cmd[1]

def directory_exists(s3, s3_res, loc):
    if(is_relative_path(loc)): # TODO
        print("directory_exists() not currently implemented to handle relative paths")
        return True

    path = ''.join(loc.split('/', 1))
    path_split = path.split('/')
    bucket_name = path_split[0]
    path = path.replace(bucket_name+"/", '')

    if(len(path.split('/')) == 1): # The location given is a bucket
        response = s3.list_buckets()
        for bucket in response['Buckets']:
            if(bucket["Name"] == path):
                return True

    if(bucket_empty(s3, bucket_name)):
        return False
    
    prefix = path + "/"
    response = s3.list_objects(Bucket=bucket_name, Prefix=prefix)
    try:
        contents = response["Contents"]
    except KeyError:
        return False
    for obj in response["Contents"]:
        if(obj["Key"].split('/')[0] == path):
            return True
        if(obj["Key"] == prefix): # Directory exists, it's just empty
            return True
    return False

def check_location(s3, s3_res, cwd, cmd): # Check if directory exists
    if(missing_arg(cmd, 2)):
        print("Usage: chlocn /<full/relative pathname of directory>")
        return False

    full_path = ""
    if(is_relative_path(cmd[1])):
        if(cwd == ""):
            bucket_name = cmd[1]
            full_path = "/"+bucket_name
        else:
            bucket_name = cwd.split('/')[1]
            full_path = cwd+"/"+cmd[1]
    else:
        path = ''.join(cmd[1].split('/', 1))
        path_split = path.split('/')
        bucket_name = path_split[0]
        full_path = cmd[1]

        # Check if last item in path is a folder (not a file)
        if(is_file(path_split)):
            print("You cannot chlocn to a file, please chlocn to a directory/folder")
            return False

    # Check if bucket exists
    if(not bucket_exists(s3_res, bucket_name)):
        print("Bucket does not exist")
        return False
    
    # Check if directory exists
    if(not directory_exists(s3, s3_res, full_path)):
        print("Directory does not exist")
        return False
    return True

# [Cloud Functions]
# 4d) Current working directory or location
# Assumptions:
# Limitations:
# TODO:

def get_cwd(cwd):
    print(cwd)

    # The following builds the success string --> <bucket name>: <full pathname of directory>
    # path_split = cwd.split('/')
    # bucket_name = path_split[1]
    # cwd_path = cwd.replace("/"+bucket_name+"/", '')
    # return_str = bucket_name + ": " + cwd_path + "/" 
    # print(return_str)

# [Cloud Functions]
# 4e) List buckets, directories, objects
# Assumptions: If list is given an argument, it is the full pathname
# Limitations:
# TODO: When listing a directory, it lists everything (even further down the tree)

def count_buckets(s3):
    count = 0
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        # buckets.append(bucket["Name"])
        count += 1
    return count

def list_buckets(s3):
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(bucket["Name"]+"  ", end="")

def content_dne(content, content_arr):
    for i in range(0, len(content_arr)):
        if(content == content_arr[i]):
            return False
    return True

def print_list(arr):
    for i in range(0, len(arr)):
        print(arr[i]+" ", end="")

def list_bucket_contents(s3, s3_res, bucket_name):
    if(not bucket_empty(s3, bucket_name)): # Check that bucket it not empty
        top_level_contents = []
        response = s3.list_objects(Bucket=bucket_name)
        for obj in response["Contents"]:
            if(len(obj["Key"].split('/')) >= 2):
                if(len(obj["Key"].split('/')) == 2 and obj["Key"].split('/')[1] == ""):
                    # Folder in top level
                    if(content_dne(obj["Key"], top_level_contents)):
                        top_level_contents.append(obj["Key"])
                else:
                    # Multi-level directories (need trimming) in top level
                    if(content_dne(obj["Key"].split('/')[0], top_level_contents)):
                        top_level_contents.append(obj["Key"].split('/')[0])
            else:
                # Files in top level
                if(content_dne(obj["Key"], top_level_contents)):
                    top_level_contents.append(obj["Key"])
        print_list(top_level_contents)
        return True
    return False

def list_path_contents(s3, path, bucket_name):
    prefix = path.replace(bucket_name+"/", '') + "/"
    top_level_contents = []
    response = s3.list_objects(Bucket=bucket_name, Prefix=prefix)

    try:
        contents = response["Contents"]
    except KeyError:
        return False

    for obj in response["Contents"]:
        if(len(obj["Key"].split('/')) >= 3): # If len == 2 and obj["Key"].split('/')[1] == "", it's the prefix
            # Multi-level directories (need trimming) in top level
            folder = obj["Key"].split('/')[1] + "/"
            if(folder != (prefix.split('/')[-2]+"/")): # Don't list the folder you want to list contents of
                if(content_dne(folder, top_level_contents)):
                    top_level_contents.append(folder)
        else:
            # Files in top level
            file_obj = obj["Key"].split('/')[-1]
            if(content_dne(file_obj, top_level_contents) and is_file(obj["Key"].split('/'))):
                top_level_contents.append(file_obj)
    if(len(top_level_contents) > 0):
        print_list(top_level_contents)
        return True
    return False

def list_bdo(s3, s3_res, cwd, cmd):

    # List from cwd (list with no following argument)
    if(len(cmd) == 1):
        path = ''.join(cwd.split('/', 1))
        path_split = path.split('/')
        bucket_name = path_split[0]
        current_directory = cwd.replace('/', '')
        
        # Listing existing buckets in a new session
        if(cwd == ""):
            list_buckets(s3)
        # The cwd in a bucket
        elif(current_directory == bucket_name):
            if(list_bucket_contents(s3, s3_res, bucket_name)):
                print("") # Formatting
                return
        else:
            # List given path
            if(list_path_contents(s3, path, bucket_name)):
                print("") # Formatting
                return
        print("") # Formatting
        return
    
    # List with a given path (full path)
    else:
        # List at root (list buckets)
        if(cmd[1] == "/" or cmd[1] == "~"):
            list_buckets(s3)
        else:

            if(is_relative_path(cmd[1])):
                path = ''.join(cwd.split('/', 1))
            else:
                path = ''.join(cmd[1].split('/', 1))
            path_split = path.split('/')
            bucket_name = path_split[0]
            
            # List given bucket
            if(path == bucket_name):
                if(list_bucket_contents(s3, s3_res, bucket_name)):
                    print("") # Formatting
                    return
            else:
                # List given path
                if(list_path_contents(s3, path, bucket_name)):
                    print("") # Formatting
                    return
        print("") # Formatting
        return
    print("Cannot list contents of this S3 location.")

# [Cloud Functions]
# 4g) Delete object
# Assumptions: if no / before second argument, the person is referrencing object from cwd
# Limitations:
# TODO: delete files

def folder_obj_count(s3_res, bucket_name, path):
    count = 0
    bucket = s3_res.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=path):
        count += 1
    return count-1 # Subtract one since the path itself is also counted

def delete_obj(s3, s3_res, cwd, cmd):
    if(missing_arg(cmd, 2)):
        print("Usage: s3delete /<full/relative pathname of object>")
        return
    
    path_split = cmd[1].split('/') # ==> ['', <path split up>]
    bucket_name = cwd.split('/')[1]

    if(len(path_split) == 2 and path_split[1] == bucket_name):
        print("Cannot perform delete on a bucket (please use 'delete_bucket' to delete buckets).")
        return
    else:
        path = ""
        if(is_relative_path(cmd[1])): # Relative path given
            path = ''.join(cwd.split('/', 1)) + "/" +cmd[1]
        else: # Full path given
            path = ''.join(cmd[1].split('/', 1))
        path_split = path.split('/')
        bucket_name = path_split[0]

        if(is_file(path_split)): # Path leads to a file
            if(not bucket_exists(s3_res, bucket_name)):
                print("Cannot perform delete: bucket does not exist")
                return
            
            filename = path_split[-1]
            # response = s3.delete_object(Bucket=bucket_name, Key=filename)
            response = s3_res.Object(bucket_name, filename).delete()
        else: # Path is a folder
            if(not is_relative_path(cmd[1])): # directory_exists() not currently implemented to handle relative paths
                if(not directory_exists(s3, s3_res, cmd[1])):
                    print("Cannot perform delete: directory does not exist")
                    return

            if(folder_obj_count(s3_res, bucket_name, path) > 0):
                print("Cannot perform delete: directory/folder is not empty")
                return
            
            folder = path.replace(bucket_name+"/", '') + "/"
            print(folder)
            response = s3.delete_object(Bucket=bucket_name, Key=folder)

# [Cloud Functions]
# 4h) Delete bucket
# Assumptions:
#   - Bucket must be empty (it will not: delete all objects within the bucket, then the bucket itself)
# Limitations: Error occurs when trying to delete a bucket that does not exist
# TODO:

def bucket_empty(s3, bucket_name):
    response = s3.list_objects(Bucket=bucket_name)
    try:
        contents = response["Contents"]
    except KeyError:
        return True
    return False

def delete_bucket(s3, s3_res, cwd, cmd):
    if(missing_arg(cmd, 2)):
        print("Usage: delete_bucket /<bucket_name>")
        return
    
    delete_bucket = cmd[1].replace('/', '')
    # Cannot delete a bucket if you're currently in the bucket
    if(cwd != ""): # User is not at root
        cwd_bucket_name = (cwd.split('/')[1]).replace('/', '')
        if(cwd_bucket_name == delete_bucket):
            print("Cannot delete the bucket you are currently in")
            return
    
    # # Cannot delete bucket that does not exist -> TODO
    # if(not bucket_exists(s3, delete_bucket)):
    #     print("Cannot delete a bucket that does not exist")
    #     return
    
    # Cannot delete bucket if it's not empty
    if(not bucket_empty(s3, delete_bucket)):
        print("Cannot delete a non-empty bucket")
        return
    
    s3.delete_bucket(Bucket=delete_bucket)
