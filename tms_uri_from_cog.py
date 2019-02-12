import os
from rf_client import RFClient
import ssl
import configparser
import boto3
import click

def get_matching_s3_objects(bucket, prefix='', suffix=''):
    """
    Generate objects in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)

        try:
            contents = resp['Contents']
        except KeyError:
            return

        for obj in contents:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield obj

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj['Key']
        
def get_full_s3_uri(bucket, prefix='', suffix=''):
    """
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    
    Returns the full uri
    """
    for pre in get_matching_s3_keys(bucket, prefix, suffix):
        yield (os.path.splitext(os.path.split(pre)[-1])[0], "s3://"+bucket+'/'+pre)

@click.command()
@click.argument('bucket')
@click.argument('prefix')
@click.argument('suffix')
def main(bucket, prefix='', suffix=''):
    """
    Takes as inputs a bucket and prefix that specify
    the location on s3 that contains COGs that can be 
    used to make overviews, allowing COGs to be visualized 
    on rasterfoundry next to planet imagery and other COGs. 
    Suffix is specified as the ending chracters to filter files 
    by like 'iteration12.tif'.

    Example: python tms_uri_from_cog.py activemapper classified-images/GH0421189_GH0493502 iteration12.tif
    """
    # disable ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    # read config
    config = configparser.ConfigParser()
    config.read('cfg/config.ini')

    rfclient = RFClient(config)
    
    for scene_id, scene_uri in get_full_s3_uri(bucket, prefix, suffix):
        try:
             rfclient.create_tms_uri(scene_id,scene_uri)

if __name__ == '__main__':
    main()
