import asyncio
import json
import os
from datetime import date
from random import randint

from fastapi import FastAPI, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from agents.BaseAgent import History, Message
from chat_workflow import handle_response, step_conversation
from humanity_client.client import Client

app = FastAPI(
    title="AI Chat Platform",
)

dir_path = os.path.dirname(os.path.realpath(__file__))

app.mount("/static", StaticFiles(directory=f"{dir_path}/UI/static"), name="static")

conversations = {}
scratchpad = {}
sessions = {}


@app.get(
    "/",
    summary="Load Dashboard",
    response_class=HTMLResponse,
)
def load_root_dashboard() -> str:
    with open(f'{dir_path}/UI/home.html', 'r') as home_file:
        return home_file.read()


@app.get(
    "/admin",
    summary="Admin Dashboard",
    response_class=HTMLResponse,
)
def load_admin_dashboard() -> str:
    with open(f'{dir_path}/UI/home.html', 'r') as home_file:
        return home_file.read()


@app.get(
    "/app/{rest_of_path:path}",
    summary="Load Dashboard",
    response_class=HTMLResponse,
)
def load_dashboard() -> str:
    with open(f'{dir_path}/UI/home.html', 'r') as home_file:
        return home_file.read()


def create_session(client):
    session_id = len(sessions) + randint(0, 1000000)
    sessions[session_id] = client
    return session_id


class NeedLoginException(Exception):
    pass


@app.exception_handler(NeedLoginException)
def raise_need_login_and_delete_cookie(req: Request, exc: NeedLoginException):
    resp = JSONResponse(
        status_code=401,
        content={'detail': 'need login'}
    )
    resp.delete_cookie('session_id')  # This cookie deletion will be applied
    return resp


def get_session_id( request: Request, response: Response ):
    session_id = request.cookies.get("session_id")
    if session_id is None or int(session_id) not in sessions:
        with open( f'{dir_path}/sessions.json', 'r' ) as sessions_file:

            disk_sessions = json.load(sessions_file)
        if str(session_id) in disk_sessions:
            return int( session_id )
        raise NeedLoginException()
    return int( session_id )


async def get_conversation_for_session_id( session_id ):
    if session_id not in conversations:
        client = get_authenticated_client_from_session_id( session_id )
        status, me_response = await client.Employees.get_me()
        conversations[ session_id ] = [
            {
                'role': 'assistant',
                'content': f"Hello {me_response['data']['firstname']}, How can I assist you today?"
            }
        ]
    return conversations[session_id]

async def get_conversation_for_session_id_v2( session_id ):
    if session_id not in conversations:
        client = get_authenticated_client_from_session_id( session_id )
        status, me_response = await client.Employees.get_me()
        conversations[ session_id ] = History(
            conversation = [
                Message(
                    role= 'assistant',
                    content= f"Hello {me_response['data']['firstname']}, How can I assist you today?"
                )
            ]
        )
    return conversations[session_id]


def get_authenticated_client_from_session_id(session_id):
    if session_id not in sessions:
        with open( f'{dir_path}/sessions.json', 'r' ) as sessions_file:
            disk_sessions = json.load( sessions_file )
            authentication_creds = disk_sessions[str(session_id)]
        sessions[session_id] = Client( authentication_creds = authentication_creds )

    # Get the user from the session
    return sessions.get(session_id)


def authenticate_user(username, password):
    client = Client()
    status = asyncio.run( client.login( username, password ) )

    if status != 200:
        raise NeedLoginException()
    return client


@app.post(
    "/log-in"
)
def login(username: str = Body(), password: str = Body()):
    client = Client()
    success = asyncio.run( client.login( username, password ))
    if not success:
        return JSONResponse( content = { "message": "Logged in failed" } )

    session_id = create_session(client)
    with open( f'{dir_path}/sessions.json', 'w+' ) as sessions_file:
        try:
            file_data = json.load( sessions_file )
        except:
            file_data = {}
        file_data[session_id] = client.authentication_creds
        json.dump( file_data, sessions_file )

    response = JSONResponse( content = {"message": "Logged in successfully", "session_id": session_id} )
    response.set_cookie( 'session_id', session_id )
    return response

@app.post(
    "/log-out"
)
def logout(
    session_id = Depends(get_session_id)
):
    with open( f'{dir_path}/sessions.json', 'w+' ) as sessions_file:
        try:
            file_data = json.load( sessions_file )
        except:
            file_data = {}
        try:
            del sessions[ session_id ]
        except:
            pass
        try:
            del file_data[ session_id ]
        except:
            pass
        json.dump( file_data, sessions_file )

    response = JSONResponse( content = {"message": "Logged Out"} )
    response.delete_cookie( 'session_id' )
    return response


@app.post(
    "/chat/load",
)
async def load_chat(
    session_id = Depends(get_session_id)
):
    return {
        'conversation': await get_conversation_for_session_id(session_id)
    }


@app.post(
    "/chat/v1/send",
)
async def send_chat(
    session_id = Depends(get_session_id),
    message: str = Body(),
    extras: dict = Body(None)
):
    conversation = await get_conversation_for_session_id(session_id)
    conversation.append( {
        'role': 'user',
        'content': message
    })
    client = sessions[ session_id ]
    if session_id not in scratchpad:
        scratchpad[session_id] = []
    user_scratchpad = scratchpad[session_id]
    today = date.today()

    for attempt in range( 5 ):
        response_body = await step_conversation( conversation, today )
        return_to_client = await handle_response(
            client,
            conversation,
            user_scratchpad,
            response_body
        )
        if return_to_client:
            break

    with open( f'{dir_path}/conversation.json', 'w' ) as output_file:
        json.dump( conversation, output_file, indent = 4, default=jsonable_encoder )
    return {
        'conversation': conversation
    }


@app.post(
    "/chat/v2/send",
)
async def send_chat(
    session_id = Depends(get_session_id),
    message: str = Body(),
    extras: dict = Body(None)
):
    conversation = await get_conversation_for_session_id_v2(session_id)
    from agents.RouterAgent import RootRouterAgent
    agent = RootRouterAgent(
        get_authenticated_client_from_session_id(session_id),
    )

    conversation.append( {
        'role': 'user',
        'content': message
    })
    client = sessions[ session_id ]
    if session_id not in scratchpad:
        scratchpad[session_id] = []
    user_scratchpad = scratchpad[session_id]
    today = date.today()

    for attempt in range( 5 ):
        response_body = await step_conversation( conversation, today )
        return_to_client = await handle_response(
            client,
            conversation,
            user_scratchpad,
            response_body
        )
        if return_to_client:
            break

    with open( f'{dir_path}/conversation.json', 'w' ) as output_file:
        json.dump( conversation, output_file, indent = 4, default=jsonable_encoder )
    return {
        'conversation': conversation
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    print(f"Starting server at http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
