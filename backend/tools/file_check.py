def allowed_file(file, allowed_extensions, max_content_length):
    extension_allowed = '.' in file.filename and \
                        file.filename.rsplit('.', 1)[1].lower() in allowed_extensions

    size_allowed = len(file.read()) <= max_content_length
    file.seek(0)

    return extension_allowed and size_allowed