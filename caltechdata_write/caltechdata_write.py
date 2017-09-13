from requests import session
from caltechdata_write import customize_schema
import json
import os

def send_s3(filepath,token):
    s3surl = "https://cd-sandbox.tind.io/tindfiles/sign_s3/"
    chkurl = "https://cd-sandbox.tind.io/tindfiles/md5_s3"

    headers = { 'Authorization' : 'Bearer %s' % token }

    c = session()

    response = c.get(s3surl,headers=headers)
    jresp = response.json()
    data = jresp['data']

    bucket = jresp['bucket']
    key = data['fields']['key']
    policy = data['fields']['policy']
    aid = data['fields']['AWSAccessKeyId']
    signature = data['fields']['signature']
    url = data['url']

    infile = open(filepath,'rb')
    size = infile.seek(0,2)
    infile.seek(0,0) #reset at beginning

    s3headers = { 'Host' : bucket+'.s3.amazonaws.com',\
            'Date' : 'date',\
            'x-amz-acl' : 'public-read',\
            'Access-Control-Allow-Origin' : '*' }

    form = ( ( 'key', key )
            , ("acl", "public-read")
            , ('AWSAccessKeyID', aid)
            , ('policy', policy)
            , ('signature', signature)
            , ('file', infile ))

    c = session()
    response = c.post(url,files=form, headers=s3headers)
    if(response.text):
        raise Exception(response.text)

    response = c.get(chkurl+'/'+bucket+'/'+key,headers=headers)
    md5 = response.json()["md5"]
    filename = filepath.split('/')[-1]

    fileinfo = { "url" : key,\
            "filename" : filename,\
            "md5" : md5,"size" : size }

    return(fileinfo)

def Caltechdata_write(metadata,token,files=[]):

    #If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]

    fileinfo=[]

    for f in files:
        fileinfo.append(send_s3(f,token))

    url = "https://cd-sandbox.tind.io/submit/api/create/"

    headers = { 'Authorization' : 'Bearer %s' % token }

    newdata = customize_schema.customize_schema(metadata)
    newdata['files']=fileinfo

    dat = { 'record': json.dumps(newdata) }

    c = session()
    response = c.post(url,headers=headers,data=dat)
    print(response.text)
