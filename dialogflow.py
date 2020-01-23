import dialogflow_v2
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
import json
import config

def getResponseDialogFlow(userId: str, text_to_be_analyzed: str):

    credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON))
    session_client = dialogflow_v2.SessionsClient(credentials=credentials)
    session = session_client.session_path(config.DIALOG_FLOW_JSON['project_id'], userId)

    text_input = dialogflow_v2.types.TextInput(text=text_to_be_analyzed, language_code='ru-RU')
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