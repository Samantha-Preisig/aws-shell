# aws-shell

## Running the shell
- Make sure to have your aws_access_key_id and aws_secret_access_key set up in an `S5-S3.conf` file. The file should be set up as the following:
```
[default]
region = ca-central-1
aws_access_key_id = <your aws_access_key_id>
aws_secret_access_key = <your aws_secret_access_key>
```

## Assumptions:
- Full paths must start with `/`
- Relative paths don't start with `/` (ex. test_folder/test.txt)
- When creating buckets, there are no specific permissions set (other than region, everything is default)
- When deleting folders and buckets, they must be empty

## Limitations:
### `list`:
- `-l` flag is not implemented
### `s3copy`:
- Only works with full paths given
### `delete_bucket`:
- Error occurs when you try to delete a bucket that doesn't exist