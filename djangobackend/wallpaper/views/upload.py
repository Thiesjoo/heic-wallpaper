from rest_framework.decorators import api_view
from rest_framework.response import Response

from wallpaper.models import Wallpaper, WallpaperStatus
from wallpaper.services import s3_service
from wallpaper.services.s3_service import allowed_file, ALLOWED_EXTENSIONS, get_extension, \
    determine_type_from_extension, ADMIN_MAX_FILE_SIZE, DEFAULT_MAX_FILE_SIZE

from wallpaper.tasks import handle_all_images

@api_view(['POST'])
def upload_view(request):
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

    max_size = ADMIN_MAX_FILE_SIZE if request.user.is_superuser else DEFAULT_MAX_FILE_SIZE
    presigned_data, uid = s3_service.get_presigned_post_url(file_type, max_size)

    wallpaper = Wallpaper.objects.create(
        uid=uid,
        name=file_name,
        owner=request.user,
        status=WallpaperStatus.UPLOADING,
        type=determine_type_from_extension(get_extension(file_name)),
    )

    wallpaper.save()

    return Response({
        'data': presigned_data,
        'id': wallpaper.id,
    })

@api_view(['POST'])
def upload_complete(request):
    id = request.data.get('id')

    if id is None:
        return Response({
            'error': 'id is required'
        }, status=400)

    wallpaper = Wallpaper.objects.get(id=id)
    if wallpaper is None or wallpaper.owner != request.user:
            # or wallpaper.status != WallpaperStatus.UPLOADING:
        return Response({
            'error': 'invalid uid'
        }, status=400)

    if not s3_service.file_exists(wallpaper.uid):
        return Response({
            'error': 'invalid uid'
        }, status=400)

    wallpaper.status = WallpaperStatus.PROCESSING
    wallpaper.save()

    task = handle_all_images.delay(wallpaper.uid, wallpaper.type)

    return Response({
        'data': 'ok',
    }, status=202)