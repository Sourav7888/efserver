from io import BytesIO
from django.core.files.base import ContentFile


def upload_model_document(model, doc_field: str, file_name: str, template: bytes):
    """
    Upload the document to the  model document field
    """
    buffer = BytesIO()
    buffer.write(template)
    content = ContentFile(buffer.getvalue())
    model = getattr(model, doc_field)
    model.save(file_name, content)
