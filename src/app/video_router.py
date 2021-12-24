from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse

from src.video.video import CameraStream, get_available_camera_device


video_router = APIRouter()

camera_devices = get_available_camera_device()
camera_stream = CameraStream(src=camera_devices[0], add_date=False)


@video_router.get("/")
def video_endpoint():
    if not camera_stream.stream_running:
        camera_stream.start()
    return StreamingResponse(
        camera_stream.get_frame(),
        media_type='multipart/x-mixed-replace; boundary=frame')

@video_router.get("/reset")
def video_endpoint():
    camera_stream.stop()
    return Response(status_code=status.HTTP_200_OK)
