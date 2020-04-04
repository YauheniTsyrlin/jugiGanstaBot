import dialogflow_v2
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
import json
import config
import users
from google.protobuf import struct_pb2
from telebot.types import Message
from main import logger

credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON))
session_client = dialogflow_v2.SessionsClient(credentials=credentials)
contexts_client = dialogflow_v2.ContextsClient(credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON)))

def getResponseDialogFlow(session_id: str, text_to_be_analyzed: str, event: str, user: users.User):
    # clear_message_context = False

    # list_entities(config.DIALOG_FLOW_JSON['project_id'])

    contexts = get_contexts(config.DIALOG_FLOW_JSON['project_id'], session_id, "user")
    if not contexts:
        logger.info(f'Create context user for {session_id}')
        parameters = struct_pb2.Struct()
        if user:
            parameters['login'] = user.getLogin()
            parameters['name'] = user.getName()
        else:
            parameters['login'] = session_id
        create_context(config.DIALOG_FLOW_JSON['project_id'], session_id, "user", 1, parameters)
        

    # if message and message.reply_to_message:
    #     parameters = struct_pb2.Struct()
    #     parameters['reply_to_message_id'] = message.reply_to_message.message_id
    #     parameters['reply_to_message_username'] = message.reply_to_message.from_user.username
    #     create_context(config.DIALOG_FLOW_JSON['project_id'], session_id, "message", 1, parameters)
    #     clear_message_context = True

    session = session_client.session_path(config.DIALOG_FLOW_JSON['project_id'], session_id)

    query_input = None
    if event:
        event_input = dialogflow_v2.types.EventInput(name=event, language_code='ru-RU')
        query_input = dialogflow_v2.types.QueryInput(event=event_input)
    else:
        text_input = dialogflow_v2.types.TextInput(text=text_to_be_analyzed, language_code='ru-RU')
        query_input = dialogflow_v2.types.QueryInput(text=text_input)

    
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
        #print(response)
    except InvalidArgument:
        raise
    finally:
        pass

    # if clear_message_context:
    #     delete_context(config.DIALOG_FLOW_JSON['project_id'], session_id, "message")

    return response.query_result

def delete_context(project_id, session_id, context_id):
    context_name = contexts_client.context_path(project_id, session_id, context_id)
    contexts_client.delete_context(context_name)

def create_context(project_id, session_id, context_id, lifespan_count, parameters):
    contexts_client = dialogflow_v2.ContextsClient(credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON)))

    session_path = contexts_client.session_path(project_id, session_id)
    context_name = contexts_client.context_path(
        project_id, session_id, context_id)

    context = dialogflow_v2.types.Context(
        name=context_name, lifespan_count=lifespan_count, parameters=parameters)

    response = contexts_client.create_context(session_path, context)

def get_contexts(project_id, session_id, name):
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

# def get_entity(project_id, session_id, name):
#     entity_client = dialogflow_v2.EntityTypesClient(credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON)))
#     name_entity = entity_client.entity_type_path(project_id, session_id, name)
#     try:
#         entity = entity_client.get_entity_type(name_entity)
#         if entity:
#             # for field, value in context.parameters.fields.items():
#             #     if value.string_value:
#             #         #print('\t{}: {}'.format(field, value))
#             print(f'entity {entity.name} найден')
#             return entity
#         else:
#             print(f'entity {entity.name} не найден')
#             return None
#     except:
#         return None

# def list_entities(project_id, entity_type_id='4bf591fa-680d-4477-a91e-079ead57246b'):
#     entity_types_client = dialogflow_v2.EntityTypesClient(credentials = (service_account.Credentials.from_service_account_info(config.DIALOG_FLOW_JSON)))

#     parent = entity_types_client.entity_type_path(
#         project_id, entity_type_id)

#     entities = entity_types_client.get_entity_type(parent).entities

#     for entity in entities:
#         print('Entity value: {}'.format(entity.value))
#         print('Entity synonyms: {}\n'.format(entity.synonyms))
# # [END dialogflow_list_entities]

