import dialogflow_v2
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
import json
import config
import users
from google.protobuf import struct_pb2

def getResponseDialogFlow(session_id: str, text_to_be_analyzed: str, user: users.User):

    contexts = get_contexts(config.DIALOG_FLOW_JSON['project_id'], session_id, "user")
    if not contexts:
        print(f'Create context user for {session_id}')
        parameters = struct_pb2.Struct()
        parameters['login'] = user.getLogin()
        parameters['name'] = user.getName()
        create_context(config.DIALOG_FLOW_JSON['project_id'], session_id, "user", 60, parameters)

    credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON))
    session_client = dialogflow_v2.SessionsClient(credentials=credentials)
    session = session_client.session_path(config.DIALOG_FLOW_JSON['project_id'], session_id)

    text_input = dialogflow_v2.types.TextInput(text=text_to_be_analyzed, language_code='ru-RU')
    query_input = dialogflow_v2.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
        # print(response.query_result)
    except InvalidArgument:
        raise
    
    return response.query_result

def create_context(project_id, session_id, context_id, lifespan_count, parameters):
    import dialogflow_v2 as dialogflow
    contexts_client = dialogflow.ContextsClient(credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON)))

    session_path = contexts_client.session_path(project_id, session_id)
    context_name = contexts_client.context_path(
        project_id, session_id, context_id)

    context = dialogflow.types.Context(
        name=context_name, lifespan_count=lifespan_count, parameters=parameters)

    response = contexts_client.create_context(session_path, context)

def get_contexts(project_id, session_id, name):
    import dialogflow_v2 as dialogflow
    contexts_client = dialogflow.ContextsClient(credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON)))
    name_context = contexts_client.context_path(project_id, session_id, name)
    try:
        context = contexts_client.get_context(name_context)
        if context:
            # for field, value in context.parameters.fields.items():
            #     if value.string_value:
            #         #print('\t{}: {}'.format(field, value))
            return context
        else:
            print(f'Context {context.name} не найден')
            return None
    except:
        return None