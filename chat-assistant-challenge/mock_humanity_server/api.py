import json
import os
from fastapi import FastAPI, Body, Depends, APIRouter

web_app = FastAPI(
    title = "Humanity Mock API",
)
app = web_app

dir_path = os.path.dirname( os.path.realpath( __file__ ) )

conversations = {}
scratchpad = {}
sessions = {}

@app.post(
    '/api/'
)
async def login():
    return {
        'status': 1,
        'message': 'Login complete',
        'token': 'blah'
    }


v2_router = APIRouter()
def load_response(file_path):
    with open( file_path, "r" ) as file:
        return json.load( file )


@v2_router.get(
    '/me'
)
async def get_me():
    return load_response('get_me.json')

@v2_router.get(
    '/shifts'
)
async def get_shifts(
    start_date: str,
    end_date: str,
    mode: str,
    employees: str
):
    return load_response('get_shifts.json')

@v2_router.get(
    '/shifts/{shift_id:int}/'
)
async def get_shifts():
    return load_response('get_shift_SHIFT_ID.json')

@v2_router.get(
    '/employees'
)
async def get_shifts():
    return load_response('get_employees.json')

@v2_router.get(
    '/shifts/{shift_id:int}/tradelist_v2'
)
async def get_shifts():
    return load_response('get_shift_SHIFT_ID_tradelist_v2.json')

@v2_router.post(
    '/trade'
)
async def get_shifts():
    return load_response('post_trades.json')

@v2_router.get(
    '/leave-types'
)
async def get_shifts():
    return load_response('get_leave_types.json')

@v2_router.post(
    '/leaves'
)
async def get_shifts():
    return load_response('post_leaves.json')


app.include_router( v2_router, prefix="/api/v2" )

if __name__ == "__main__":
    import uvicorn
    print("Starting mock Humanity server at http://localhost:8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)