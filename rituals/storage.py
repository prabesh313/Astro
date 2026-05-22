from cloudinary_storage.storage import MediaCloudinaryStorage
import cloudinary.uploader
import cloudinary.utils
class AudioCloudinaryStorage(MediaCloudinaryStorage):
    def _upload(self, name, content):
        response = cloudinary.uploader.upload(
            content,
            resource_type="video",
            use_filename=True,
            unique_filename=True,
            folder="mantras/audio/",
        )
        return response

    def url(self, name):
        cloudinary_name = name
        if cloudinary_name.startswith('media/'):
            cloudinary_name = cloudinary_name[len('media/'):]
        url, _ = cloudinary.utils.cloudinary_url(
            cloudinary_name,
            resource_type="video",
        )
        return url


class PDFCloudinaryStorage(MediaCloudinaryStorage):
    def _upload(self, name, content):
        response = cloudinary.uploader.upload(
            content,
            resource_type="raw",
            use_filename=True,
            unique_filename=True,
            folder="books/pdfs/",
        )
        return response

    def url(self, name):
        cloudinary_name = name
        if cloudinary_name.startswith('media/'):
            cloudinary_name = cloudinary_name[len('media/'):]
        url, _ = cloudinary.utils.cloudinary_url(
            cloudinary_name,
            resource_type="raw",
            
        )
        return url