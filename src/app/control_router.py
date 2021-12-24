from fastapi import APIRouter, Request, Response, status
from src.video.control import controller


control_router = APIRouter()



@control_router.post("/up")
async def up_endpoint():
    try:
        controller.up()
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@control_router.post("/down")
async def up_endpoint():
    try:
        controller.down()
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@control_router.post("/left")
async def up_endpoint():
    try:
        controller.left()
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@control_router.post("/right")
async def up_endpoint():
    try:
        controller.right()
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
