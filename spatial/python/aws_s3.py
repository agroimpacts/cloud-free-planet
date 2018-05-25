"""
AWS_S3

this class is added to support operations with S3 on AWS, including
 1. create s3 session and client
 2. list the objects that have the given prefix and given suffix in the given bucket,
 3. upload local file to s3 bucket
 4. delete file on s3 bucket
 5. generate a presigned url for a file on s3 bucket
"""

import boto3
import boto3.session
import pandas as pd
from io import BytesIO


class AWS_S3():
    def __int__(self):
        self.s3_client = None
        self.s3_resource = None
        self.aws_session = None

    #please set the aws credentials in "~/.aws/credentials" file
    def create_client(self, _region_name='us-east-1'):
        self.aws_session = boto3._get_default_session()
        self.s3_client = boto3.client('s3', region_name=_region_name)
        self.s3_resource = boto3.resource('s3', region_name=_region_name)

    #please use the above method, which is more secure
    def create_client_with_access(self, _aws_access_key_id, _aws_secret_access_key, _region_name='us-east-1'):
        #customize session
        self.aws_session = boto3.session.Session()
        self.s3_client = self.aws_session.client('s3', aws_access_key_id=_aws_access_key_id,
                                                 aws_secret_access_key=_aws_secret_access_key,
                                                 region_name=_region_name)
        self.s3_resource = self.aws_session.resource('s3', aws_access_key_id=_aws_access_key_id,
                                                 aws_secret_access_key=_aws_secret_access_key,
                                                 region_name=_region_name)

    ########################
    #search any files that have the given prefix / suffix in the given bucket
    #suffix could be None, or a string  or a list of string
    #output: return a list
    def list_objects(self, bucket, prefix, suffix=None):
        res = []
        if self.s3_resource is not None:
            ###############################
            #old version
            #might not return all the files, limit to a a maximum number
            #objs = self.s3_client.list_objects(Bucket=bucket, Prefix=prefix)
            # if 'Contents'in objs:
            #     for obj in objs['Contents']:
            #         #if no suffix given, add all objects with the prefix
            #         if suffix is None:
            #             res.append(str(obj['Key']))
            #         else:
            #             #add all objects that ends with the given suffix
            #             if type(suffix) is list:
            #                 for _suffix in suffix:
            #                     if obj['Key'].endswith(_suffix):
            #                         res.append(str(obj['Key']))
            #                         break;
            #             else:
            #                 #suffix is a single string
            #                 if obj['Key'].endswith(suffix):
            #                     res.append(str(obj['Key']))
            ##############################
            my_bucket = self.s3_resource.Bucket(bucket)
            for obj in my_bucket.objects.filter(Prefix=prefix):
                #if no suffix given, add all objects with the prefix
                if suffix is None:
                    res.append(str(obj.key))
                else:
                    #add all objects that ends with the given suffix
                    if type(suffix) is list:
                        for _suffix in suffix:
                            if obj.key.endswith(_suffix):
                                res.append(str(obj.key))
                                break;
                    else:
                        #suffix is a single string
                        if obj.key.endswith(suffix):
                            res.append(str(obj.key))
        else:
            print 'Warning: please firstly create s3 client using create_client '
        return res

    ###########################################
    #check if a file already exist in the given bucket
    #output: return True/False
    def is_obj_exist_on_s3(self, bucket, obj):
        if self.s3_client is not None:
            objs = self.s3_client.list_objects(Bucket=bucket, Prefix=obj)
            if 'Contents' in objs and len(objs['Contents']) > 0 and obj == str(objs['Contents'][0]['Key']):
                return True
        else:
            print 'Warning: please firstly create s3 client using create_client '
        return False

    #########################################
    #generate presigned url to access a given obj in the given bucket
    #output: return the presigned url
    def gen_presigned_url(self, bucket, obj):
        presigned_url = None
        if self.s3_client is not None:
            presigned_url = self.s3_client.generate_presigned_url(ClientMethod='get_object',
                                                                  Params={'Bucket': bucket, 'Key': obj})
        else:
            print 'Warning: please firstly create s3 client using create_client '
        return presigned_url

    ###############################
    #upload local file to S3
    #output: None
    def upload_file_to_s3(self, bucket, local_file, des_obj_on_s3):
        # upload local file to s3
        if self.s3_client is not None:
            self.s3_client.upload_file(local_file, bucket, des_obj_on_s3)
        else:
            print 'Warning: please firstly create s3 client using create_client '

    #################################
    #delete a given object in a given bucket
    #output: None
    def delete_file_on_s3(self, bucket, obj_on_s3):
        # upload local file to s3
        if self.s3_client is not None:
            self.s3_client.delete_object(bucket, obj_on_s3)
        else:
            print 'Warning: please firstly create s3 client using create_client '


    def pd_read_csv_on_s3(self, bucket, obj_on_s3, _header=0):
        """
            This func is to read a csv file on s3  bucket into a pandas dataframe
            Args:
                bucket: the s3 bucket name , e.g., activemapper
                obj_on_s3: the path of the file (without bucket name), e.g., imagery/test.csv
            Returns:
                None or a pandas dataframe
        """
        if self.is_obj_exist_on_s3(bucket, obj_on_s3):
            obj = self.s3_client.get_object(Bucket=bucket, Key=obj_on_s3)
            pd_dataframe = pd.read_csv(BytesIO(obj['Body'].read()), header=_header)
            return pd_dataframe
        return None



    def put_pd_df_to_csv_on_s3(self, pd_df, bucket, obj_on_s3,_index=False):
        """
            This func is to write a pandas dataframe to a csv file on s3 bucket

            Args:
                pd_df: a pandas dataframe
                bucket: the s3 bucket name , e.g., activemapper
                obj_on_s3: the path of the file (without bucket name), e.g., imagery/test.csv

        """
        cvs_buffer = BytesIO()
        pd_df.to_csv(cvs_buffer, index=_index)
        self.s3_resource.Object(bucket, obj_on_s3).put(Body=cvs_buffer.getvalue())