import os
import boto3
import json
from dotenv import load_dotenv

load_dotenv()

session = boto3.Session(
    profile_name=os.getenv("AWS_PROFILE"),
    region_name=os.getenv("AWS_REGION")
)

bedrock = session.client("bedrock-runtime")

def get_embedding(text):
    payload = {
        "inputText": text
    }

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(payload),
        contentType="application/json"
    )

    result = json.loads(response["body"].read())
    return result["embedding"]
