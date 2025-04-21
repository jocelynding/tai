import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from starlette.responses import RedirectResponse

app = FastAPI()


async def fake_video_streamer():
    for i in range(10):
        yield b"some fake video bytes"


@app.post("/test")
async def test_output():
    return StreamingResponse(fake_video_streamer())


@app.get("/")
def root():
    response = RedirectResponse(url="/docs")
    return response


if __name__ == "__main__":
    uvicorn.run("test:app", host="0.0.0.0", port=8001, reload=True)
