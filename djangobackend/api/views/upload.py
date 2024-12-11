from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Wallpaper, WallpaperStatus
from api.services import s3_service
from api.services.s3_service import allowed_file, ALLOWED_EXTENSIONS, get_extension, \
    determine_type_from_extension


@api_view(['POST'])
def uploadView(request):
    file_name = request.data.get('name')
    file_type = request.data.get('type')

    if file_name is None or file_type is None:
        return Response({
            'error': 'name and type are required'
        }, status=400)

    if not allowed_file(file_name):
        return Response({
            'error': 'Invalid file type'
        }, status=400)

    if not ALLOWED_EXTENSIONS[get_extension(file_name)] == file_type:
        return Response({
            'error': 'Invalid file type'
        }, status=400)

    presigned_data, uid = s3_service.get_presigned_post_url(file_name, file_type)

    wallpaper = Wallpaper.objects.create(
        uid=uid,
        name=file_name,
        owner=request.user,
        status=WallpaperStatus.UPLOADING,
        type=determine_type_from_extension(get_extension(file_name)),
        data={},
    )

    wallpaper.save()

    return Response({
        'data': presigned_data,
        'uid': uid,
    })

@api_view(['POST'])
def upload_complete(request):
    uid = request.data.get('uid')

    if uid is None:
        return Response({
            'error': 'uid/key is required'
        }, status=400)

    wallpaper = Wallpaper.objects.get(uid=uid)
    if wallpaper is None or wallpaper.owner != request.user:
        return Response({
            'error': 'invalid uid'
        }, status=400)

    if not s3_service.file_exists(uid):
        return Response({
            'error': 'invalid uid'
        }, status=400)

    wallpaper.status = WallpaperStatus.PROCESSING
    wallpaper.save()

    # s3_service.handle_all_images.delay(key, uid, determine_type_from_extension(
    #     get_extension(key)))

    return Response({
        'data': 'ok',
    }, status=202)