import io
import os

from PIL import Image, ImageDraw, ImageFont
from asgiref.sync import sync_to_async
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ASSETS_DIR = os.path.join(settings.BASE_DIR, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
BG_IMAGE_PATH = os.path.join(ASSETS_DIR, 'img', 'certificate_bg.png')

COLOR_GOLD_HEX = "#B48E3D"
COLOR_DARK_HEX = "#1A237E"
COLOR_GREY_HEX = "#555555"

COLOR_GOLD = colors.HexColor(COLOR_GOLD_HEX)
COLOR_DARK = colors.HexColor(COLOR_DARK_HEX)
COLOR_GREY = colors.HexColor(COLOR_GREY_HEX)


def register_pdf_fonts():
    """Реєстрація шрифтів для PDF"""
    try:
        pdfmetrics.registerFont(TTFont('GreatVibes', os.path.join(FONTS_DIR, 'GreatVibes-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Montserrat', os.path.join(FONTS_DIR, 'Montserrat-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Montserrat-Bold', os.path.join(FONTS_DIR, 'Montserrat-Bold.ttf')))
        return True
    except Exception as e:
        print(f"Font loading error: {e}")
        return False


def get_pil_font(font_name, size):
    """Отримання шрифту для PNG"""
    font_path = os.path.join(FONTS_DIR, f"{font_name}.ttf")
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        return ImageFont.load_default()


def ensure_assets_exist():
    """Створення заглушок, якщо файлів немає (щоб код не впав)"""
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        os.makedirs(FONTS_DIR, exist_ok=True)
        if not os.path.exists(os.path.dirname(BG_IMAGE_PATH)):
            os.makedirs(os.path.dirname(BG_IMAGE_PATH), exist_ok=True)


def _generate_pdf_sync(certificate):
    ensure_assets_exist()
    has_custom_fonts = register_pdf_fonts()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    try:
        c.drawImage(BG_IMAGE_PATH, 0, 0, width=width, height=height)
    except Exception:
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(20)
        c.rect(0, 0, width, height)
        c.setStrokeColor(COLOR_DARK)
        c.setLineWidth(5)
        c.rect(20, 20, width - 40, height - 40)

    cx = width / 2
    cy = height / 2

    if has_custom_fonts:
        c.setFont("Montserrat-Bold", 42)
    else:
        c.setFont("Helvetica-Bold", 42)
    c.setFillColor(COLOR_DARK)
    c.drawCentredString(cx, height - 130, "CERTIFICATE")

    if has_custom_fonts:
        c.setFont("Montserrat", 16)
    else:
        c.setFont("Helvetica", 16)
    c.setFillColor(COLOR_GOLD)
    c.drawCentredString(cx, height - 160, "OF COMPLETION")

    if has_custom_fonts:
        c.setFont("GreatVibes", 20)
    else:
        c.setFont("Helvetica-Oblique", 14)
    c.setFillColor(COLOR_GREY)
    c.drawCentredString(cx, height - 210, "This is to certify that")

    student_name = f"{certificate.user.name} {certificate.user.surname}"
    if has_custom_fonts:
        c.setFont("GreatVibes", 60)
    else:
        c.setFont("Helvetica-BoldOblique", 40)
    c.setFillColor(COLOR_DARK)
    c.drawCentredString(cx, cy + 15, student_name)

    c.setStrokeColor(COLOR_GOLD)
    c.setLineWidth(1.5)
    c.line(cx - 150, cy - 5, cx + 150, cy - 5)

    if has_custom_fonts:
        c.setFont("Montserrat", 12)
    else:
        c.setFont("Helvetica", 12)
    c.setFillColor(COLOR_GREY)
    c.drawCentredString(cx, cy - 40, "Has successfully completed the course")

    course_title = certificate.course.title
    if has_custom_fonts:
        c.setFont("Montserrat-Bold", 24)
    else:
        c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.black)
    c.drawCentredString(cx, cy - 80, course_title)

    c.setStrokeColor(COLOR_DARK)
    c.setLineWidth(1)
    c.line(cx - 70, 80, cx + 70, 80)

    if has_custom_fonts:
        c.setFont("Montserrat", 9)
    else:
        c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_DARK)
    c.drawCentredString(cx, 65, "SmartStudy Instructor")

    c.setFillColor(COLOR_GREY)
    date_str = certificate.issued_at.strftime('%B %d, %Y')

    c.drawString(60, 65, f"Date: {date_str}")
    c.drawRightString(width - 60, 65, f"ID: {certificate.certificate_id}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def _generate_png_sync(certificate):
    ensure_assets_exist()

    try:
        image = Image.open(BG_IMAGE_PATH).convert('RGB')
        target_size = (3508, 2480)
        if image.size != target_size:
            image = image.resize(target_size)
    except Exception:
        image = Image.new('RGB', (3508, 2480), color='white')
        draw_temp = ImageDraw.Draw(image)
        draw_temp.rectangle([80, 80, 3428, 2400], outline=COLOR_DARK_HEX, width=20)

    draw = ImageDraw.Draw(image)
    width, _ = image.size

    FILL_DARK = COLOR_DARK_HEX
    FILL_GOLD = COLOR_GOLD_HEX
    FILL_GREY = COLOR_GREY_HEX
    FILL_BLACK = "#000000"

    font_main_title = get_pil_font("Montserrat-Bold", 170)
    font_subtitle = get_pil_font("Montserrat-Regular", 65)
    font_certify = get_pil_font("GreatVibes-Regular", 90)
    font_name = get_pil_font("GreatVibes-Regular", 250)
    font_desc = get_pil_font("Montserrat-Regular", 50)
    font_course = get_pil_font("Montserrat-Bold", 100)
    font_footer = get_pil_font("Montserrat-Regular", 40)

    def draw_centered(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) / 2, y), text, font=font, fill=fill)

    draw_centered(550, "CERTIFICATE", font_main_title, FILL_DARK)

    draw_centered(750, "OF COMPLETION", font_subtitle, FILL_GOLD)

    draw_centered(950, "This is to certify that", font_certify, FILL_GREY)

    student_name = f"{certificate.user.name} {certificate.user.surname}"
    draw_centered(1200, student_name, font_name, FILL_DARK)

    line_y = 1500
    draw.line([(width / 2 - 600, line_y), (width / 2 + 600, line_y)], fill=FILL_GOLD, width=6)

    draw_centered(1600, "Has successfully completed the course", font_desc, FILL_GREY)
    draw_centered(1750, certificate.course.title, font_course, FILL_BLACK)

    sig_y = 2150
    draw.line([(width / 2 - 300, sig_y), (width / 2 + 300, sig_y)], fill=FILL_DARK, width=4)
    draw_centered(2170, "SmartStudy Instructor", font_footer, FILL_DARK)

    date_str = certificate.issued_at.strftime('%B %d, %Y')

    draw.text((250, 2170), f"Date: {date_str}", font=font_footer, fill=FILL_GREY)

    id_text = f"ID: {certificate.certificate_id}"
    bbox_id = draw.textbbox((0, 0), id_text, font=font_footer)
    id_w = bbox_id[2] - bbox_id[0]
    draw.text((width - 250 - id_w, 2170), id_text, font=font_footer, fill=FILL_GREY)

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
