import io

from PIL import Image, ImageDraw, ImageFont
from asgiref.sync import sync_to_async
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _generate_pdf_sync(certificate):
    """Синхронна генерація PDF"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

    p.rect(50, 50, width - 100, height - 100)

    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(width / 2, height - 150, "CERTIFICATE OF COMPLETION")

    p.setFont("Helvetica", 24)
    student_name = f"{certificate.user.name} {certificate.user.surname}"
    p.drawCentredString(width / 2, height / 2, student_name)

    p.setFont("Helvetica", 18)
    p.drawCentredString(width / 2, height / 2 - 50,
                        f"Has successfully completed the course: {certificate.course.title}")

    p.setFont("Helvetica", 12)
    p.drawString(60, 60, f"Certificate ID: {certificate.certificate_id}")
    p.drawString(width - 200, 60, f"Date: {certificate.issued_at.strftime('%Y-%m-%d')}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def _generate_png_sync(certificate):
    """Синхронна генерація PNG"""
    width, height = 1200, 850
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # font_large = ImageFont.truetype("arial.ttf", 60)
    # font_medium = ImageFont.truetype("arial.ttf", 40)
    #
    font_large = ImageFont.load_default()

    draw.rectangle([20, 20, width - 20, height - 20], outline="black", width=5)

    text_title = "CERTIFICATE OF COMPLETION"
    text_name = f"{certificate.user.name} {certificate.user.surname}"
    text_course = f"Course: {certificate.course.title}"

    draw.text((width / 2 - 150, 100), text_title, fill="black", font=font_large)
    draw.text((width / 2 - 100, 300), text_name, fill="blue", font=font_large)
    draw.text((width / 2 - 100, 400), text_course, fill="black", font=font_large)

    draw.text((50, height - 50), f"ID: {certificate.certificate_id}", fill="gray")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


async def generate_certificate_file(certificate, fmt='pdf'):
    if fmt == 'pdf':
        return await sync_to_async(_generate_pdf_sync)(certificate)
    elif fmt == 'png':
        return await sync_to_async(_generate_png_sync)(certificate)
    return None
