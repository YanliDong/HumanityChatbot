
import logging
import os
from subprocess import Popen


def start_api_server():
    import uvicorn
    os.chdir( '/code/mock_humanity_server' )
    app = "mock_humanity_server.api:app"
    host = "0.0.0.0"
    port = int( os.environ['PORT'] )
    uvicorn.run(
        app,
        host = host,
        port = port,
        reload = True,
        workers = 4
    )


if __name__ == '__main__':
    if os.environ['CONTAINER'] == 'mock_humanity_server':
        start_api_server()
    else:
        logging.error( "Unknown container" )

