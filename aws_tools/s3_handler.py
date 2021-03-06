# -*- coding: utf8 -*-
#
#  Copyright (c) 2016 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wycliffeassociates.org>

import os
import json
import boto3
import botocore

from boto3.session import Session
from general_tools.file_utils import get_mime_type


class S3Handler(object):
    def __init__(self, bucket_name=None, aws_access_key_id=None, aws_secret_access_key=None, aws_region_name='us-west-2'):
        if aws_access_key_id and aws_secret_access_key:
            session = Session(aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   region_name=aws_region_name)
            self.resource = session.resource('s3')
            self.client = session.client('s3')
        else:
            self.resource = boto3.resource('s3')
            self.client = boto3.client('s3')

        self.bucket_name = bucket_name
        self.bucket = None
        if bucket_name:
            self.bucket = self.resource.Bucket(bucket_name)

    def download_file(self, key, local_file):
        self.resource.meta.client.download_file(self.bucket_name, key, local_file)

    # Downloads all the files in S3 that have a prefix of `key_prefix` from `bucket` to the `local` directory
    def download_dir(self, key_prefix, local):
        paginator = self.client.get_paginator('list_objects')
        result = paginator.paginate(Bucket=self.bucket_name, Delimiter='/', Prefix=key_prefix)
        for subdir in result['CommonPrefixes']:
            self.download_dir(subdir['Prefix'], local)
        for f in result['Contents']:
            dir = local + os.sep + f['Key']
            if not os.path.exists(os.path.dirname(dir)):
                os.makedirs(os.path.dirname(dir))
            self.download_file(f['Key'], dir)

    def key_exists(self, key, bucket_name=None):
        if not bucket_name:
            bucket = self.bucket
        else:
            bucket = self.resource.Bucket(bucket_name)

        try:
            bucket.Object(key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                exists = False
            else:
                raise e
        else:
            exists = True

        return exists

    def copy(self, from_key, from_bucket=None, to_key=None, catch_exception=True):
        if not to_key:
            to_key = from_key
        if not from_bucket:
            from_bucket = self.bucket_name

        if catch_exception:
            try:
                return self.resource.Object(self.bucket_name, to_key).copy_from(
                    CopySource='{0}/{1}'.format(from_bucket, from_key))
            except Exception:
                return False
        else:
            return self.resource.Object(self.bucket_name, to_key).copy_from(
                CopySource='{0}/{1}'.format(from_bucket, from_key))

    def upload_file(self, path, key, cache_time=600):
        self.bucket.upload_file(path, key, ExtraArgs={'ContentType': get_mime_type(path), 'CacheControl': 'max-age={0}'.format(cache_time)})

    def get_object(self, key):
        return self.resource.Object(bucket_name=self.bucket_name, key=key)

    def get_contents(self, key, catch_exception=True):
        if catch_exception:
            try:
                return self.get_object(key).get()['Body'].read()
            except:
                return ''
        else:
            return self.get_object(key)['Body'].read()

    def redirect(self, key, location):
        self.bucket.put_object(Key=key, WebsiteRedirectLocation=location, CacheControl='max-age=0')

    def get_file_contents(self, key, catch_exception = True):
        if catch_exception:
            try:
                return self.get_object(key).get()['Body'].read()
            except Exception:
                return None
        else:
            return self.get_object(key).get()['Body'].read()

    def get_json(self, key, catch_exception = True):
        if catch_exception:
            try:
               return json.loads(self.get_file_contents(key))
            except Exception:
                return {}
        else:
            return json.loads(self.get_file_contents(key, catch_exception))

    def get_objects(self, prefix=None, suffix=None):
        filtered = []
        objects = self.bucket.objects.filter(Prefix=prefix)
        if objects:
            if suffix:
                for obj in objects:
                    if obj.key.endswith(suffix):
                        filtered.append(obj)
            else:
                filtered = objects
        return filtered

    def delete_file(self, key, catch_exception=True):
        if catch_exception:
            try:
                return self.resource.Object(self.bucket_name, key).delete()
            except Exception:
                return False
        else:
            return self.resource.Object(self.bucket_name, key).delete()
