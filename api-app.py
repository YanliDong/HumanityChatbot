import logging
import os


def start_api_server():
    import uvicorn
    os.chdir('/code')
    app = "api.api:app"
    host = "0.0.0.0"
    port = int(os.environ['PORT'])
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,
        workers=4
    )


if __name__ == '__main__':
    if os.environ.get('CONTAINER') == 'api_server':
        start_api_server()
    else:
        logging.error("Unknown container")

