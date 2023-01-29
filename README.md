# aws-shell

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