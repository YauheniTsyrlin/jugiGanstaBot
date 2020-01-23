import dialogflow_v2
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
import json

DIALOGFLOW_LANGUAGE_CODE = 'ru-RU'
GOOGLE_APPLICATION_CREDENTIALS = 'df_env.json'
dialogflow_key = json.load(open('df_env.json'))

def getResponseDialogFlow(userId: str, text_to_be_analyzed: str):

    credentials = (service_account.Credentials.from_service_account_info(dialogflow_key))
    session_client = dialogflow_v2.SessionsClient(credentials=credentials)
    session = session_client.session_path(dialogflow_key['project_id'], userId)

    text_input = dialogflow_v2.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow_v2.types.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise
    
    return response.query_result.fulfillment_text
    
    # print("Query text:", response.query_result.query_text)
    # print("Detected intent:", response.query_result.intent.display_name)
    # print("Detected intent confidence:", response.query_result.intent_detection_confidence)
    # print("Fulfillment text:", response.query_result.fulfillment_text)