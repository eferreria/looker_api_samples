from google.cloud import storage
from google.cloud import exceptions
from google.cloud import pubsub_v1
import base64
import tempfile
import pandas as pd
import zlib
import os
import io, zipfile, json, pprint
from pandas import ExcelWriter
import tempfile
import datetime
# import yagmail


# enter project name or set it as an enviromental variable. 
tmpdir = tempfile.gettempdir()
storage_client = storage.Client(project=os.environ.get('eferreria')) #add your ProjectID here
project_id = "eferreria"
topic_id = "projects/eferreria/topics/looker-report-topic"

def buckets(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    print(request_json)
    convertname(request_json)

    return request_json

def upload_bucket(request_json, path):  
    folder_name = str(request_json["scheduled_plan"]['scheduled_plan_id']) + "_" + str(request_json["scheduled_plan"]['title'])
    file_name = str(request_json["scheduled_plan"]['title'])
    bucket_name = str(request_json["form_params"]["bucket"])

    print(bucket_name)
    #list folders
    try:
        bucket = storage_client.get_bucket(bucket_name)
        full_path = folder_name + '/' + str(datetime.datetime.now()) + '_' +  file_name + '.xlsx'
        blob = bucket.blob(full_path)
        blob.upload_from_filename(path)
    
    except exceptions.GoogleCloudError as exception:
        bucket = None
        print("Bucket not found")
    
 
     
        return bucket

def post_to_topic(message):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    for n in range(1, 2):
        data_str = f"Message number {n}"
        # Data must be a bytestring
        data = data_str.encode("utf-8")
        # Add two attributes, origin and username, to the message
        future = publisher.publish(
            topic_path, data, origin="python-sample", username="gcp"
        )
        print(future.result())

    print(f"Published messages with custom attributes to {topic_path}.")

def convertname(request_json):
    with tempfile.TemporaryDirectory() as td:
        # EPHERMAL
        temp = tempfile.gettempdir()
        cur = os.path.join(td, "output.zip")
        with open(cur, 'wb') as result:
            result.write(base64.b64decode(request_json["attachment"]['data']))
            print(os.listdir(path=td))
        zip_ref = zipfile.ZipFile(cur, 'r')
        zip_ref.extractall(td)
        zip_ref.close()

        folder = os.listdir(td)

            

        file_path = os.path.join(td + '/' + folder[1])

        files = os.listdir(file_path)

        writer = pd.ExcelWriter(td + '/tabbed.xlsx', engine='xlsxwriter')
        

        for f in files:
            file_f = os.path.join(file_path, f)
            print(file_f)
            df = pd.read_csv(file_f)
            df.to_excel(writer, sheet_name=f, index=False)
        path = td + '/tabbed.xlsx'
        writer.save()
        print("Uploading dashboard...")

        print(request_json)
        print(path)
        upload_bucket(request_json, path)
        print("Upload complete!")

        print("Status: 200")
        # post_to_topic("Render Completed")
        
        # importing yagmail and its packages
        # initiating connection with SMTP server
        # email = request_json["form_params"]["email"]
        # print("Trying to send an email")
        # yag = yagmail.SMTP(os.environ.get('email'),
        #            os.environ.get('email_password'))
        # subject = request_json["form_params"]["filename"]
        # Adding Content and sending it
        # try:
        #     yag.send(to=email, subject=subject, contents='Please find the image attached', attachments=path)
        #     print("Email sent successfully")
        # except:
        #     print("Error, email was not sent")
        
        return folder
