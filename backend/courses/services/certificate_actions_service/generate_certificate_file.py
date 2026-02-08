import io
import os

from PIL import Image, ImageDraw, ImageFont
from asgiref.sync import sync_to_async
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HAS_QRCODE = False
try:
    import qrcode

    if hasattr(qrcode, 'QRCode'):
        HAS_QRCODE = True
except ImportError:
    pass

ASSETS_DIR = os.path.join(settings.BASE_DIR, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
BG_IMAGE_PATH = os.path.join(ASSETS_DIR, 'img', 'certificate_bg.png')

COLOR_GOLD_HEX = "#D4AF37"
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
    except:
        return False


def get_pil_font(font_name, size):
    """Отримання шрифту для PNG"""
    font_path = os.path.join(FONTS_DIR, f"{font_name}.ttf")
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()


def ensure_assets_exist():
    """Створення заглушок, якщо файлів немає (щоб код не впав)"""
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        os.makedirs(FONTS_DIR, exist_ok=True)
        if not os.path.exists(os.path.dirname(BG_IMAGE_PATH)):
            os.makedirs(os.path.dirname(BG_IMAGE_PATH), exist_ok=True)


def draw_decorative_border(c, width, height):
    margin = 30
    c.setStrokeColor(COLOR_GOLD)
    c.setLineWidth(3)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    inner_margin = margin + 10
    c.setStrokeColor(COLOR_DARK)
    c.setLineWidth(1)
    c.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin)

    corner_size = 40
    corners = [(margin, height - margin), (width - margin, height - margin),
               (margin, margin), (width - margin, margin)]

    c.setStrokeColor(COLOR_GOLD)
    c.setLineWidth(2)
    for x, y in corners:
        if x < width / 2 and y > height / 2:
            c.line(x, y, x + corner_size, y)
            c.line(x, y, x, y - corner_size)
        elif x > width / 2 and y > height / 2:
            c.line(x, y, x - corner_size, y)
            c.line(x, y, x, y - corner_size)
        elif x < width / 2 and y < height / 2:
            c.line(x, y, x + corner_size, y)
            c.line(x, y, x, y + corner_size)
        else:
            c.line(x, y, x - corner_size, y)
            c.line(x, y, x, y + corner_size)


def draw_decorative_border_png(draw, width, height):
    margin = 100
    draw.rectangle([margin, margin, width - margin, height - margin], outline=COLOR_GOLD_HEX, width=12)
    inner_margin = margin + 40
    draw.rectangle([inner_margin, inner_margin, width - inner_margin, height - inner_margin],
                   outline=COLOR_DARK_HEX, width=4)

    corner_size = 150
    corners = [(margin, margin), (width - margin, margin),
               (margin, height - margin), (width - margin, height - margin)]

    for x, y in corners:
        if x < width / 2 and y < height / 2:
            draw.line([(x, y), (x + corner_size, y)], fill=COLOR_GOLD_HEX, width=8)
            draw.line([(x, y), (x, y + corner_size)], fill=COLOR_GOLD_HEX, width=8)
        elif x > width / 2 and y < height / 2:
            draw.line([(x, y), (x - corner_size, y)], fill=COLOR_GOLD_HEX, width=8)
            draw.line([(x, y), (x, y + corner_size)], fill=COLOR_GOLD_HEX, width=8)
        elif x < width / 2 and y > height / 2:
            draw.line([(x, y), (x + corner_size, y)], fill=COLOR_GOLD_HEX, width=8)
            draw.line([(x, y), (x, y - corner_size)], fill=COLOR_GOLD_HEX, width=8)
        else:
            draw.line([(x, y), (x - corner_size, y)], fill=COLOR_GOLD_HEX, width=8)
            draw.line([(x, y), (x, y - corner_size)], fill=COLOR_GOLD_HEX, width=8)


def add_logo_to_pdf_svg(c, logo_path, cx, y, max_width, max_height):
    """Додає SVG логотип до PDF"""
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF

        drawing = svg2rlg(logo_path)
        if drawing:
            scale_x = max_width / drawing.width
            scale_y = max_height / drawing.height
            scale = min(scale_x, scale_y)

            drawing.width = drawing.width * scale
            drawing.height = drawing.height * scale
            drawing.scale(scale, scale)

            x = cx - (drawing.width / 2)
            renderPDF.draw(drawing, c, x, y)
    except:
        pass


def _generate_pdf_sync(certificate):
    ensure_assets_exist()
    has_custom_fonts = register_pdf_fonts()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    try:
        c.drawImage(BG_IMAGE_PATH, 0, 0, width=width, height=height)
    except:
        c.setFillColor(colors.white)
        c.rect(0, 0, width, height, fill=True, stroke=False)
        draw_decorative_border(c, width, height)

    cx = width / 2
    cy = height / 2

    logo_path = os.path.join(ASSETS_DIR, 'img', 'logo.svg')
    if os.path.exists(logo_path):
        add_logo_to_pdf_svg(c, logo_path, cx, height - 90, 80, 40)

    if HAS_QRCODE:
        try:
            import qrcode
            from reportlab.lib.utils import ImageReader
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
            qr.add_data(f"https://smartstudy.com/verify/{certificate.certificate_id}")  # TODO реалізувати перевірку сертифікату по QR коду
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            c.drawImage(ImageReader(qr_buffer), width - 90, height - 90, width=50, height=50, mask='auto')
        except:
            pass

    c.setFont("Montserrat-Bold" if has_custom_fonts else "Helvetica-Bold", 48)
    c.setFillColor(COLOR_DARK)
    c.drawCentredString(cx, height - 150, "CERTIFICATE")

    c.setFont("Montserrat" if has_custom_fonts else "Helvetica", 18)
    c.setFillColor(COLOR_GOLD)
    c.drawCentredString(cx, height - 180, "OF COMPLETION")

    c.setStrokeColor(COLOR_GOLD)
    c.setLineWidth(2)
    c.line(cx - 100, height - 195, cx + 100, height - 195)

    c.setFont("Montserrat" if has_custom_fonts else "Helvetica", 13)
    c.setFillColor(COLOR_GREY)
    c.drawCentredString(cx, cy + 70, "This is to certify that")

    student_name = f"{certificate.user.name} {certificate.user.surname}"
    c.setFont("GreatVibes" if has_custom_fonts else "Helvetica-BoldOblique", 60 if has_custom_fonts else 44)
    c.setFillColor(COLOR_DARK)
    c.drawCentredString(cx, cy + 5, student_name)

    c.setStrokeColor(COLOR_GOLD)
    c.setLineWidth(1.5)
    c.line(cx - 180, cy - 15, cx + 180, cy - 15)

    c.setFont("Montserrat" if has_custom_fonts else "Helvetica", 14)
    c.setFillColor(COLOR_GREY)
    c.drawCentredString(cx, cy - 60, "has successfully completed the course:")

    course_title = certificate.course.title
    c.setFont("Montserrat-Bold" if has_custom_fonts else "Helvetica-Bold", 24)
    c.setFillColor(COLOR_DARK)
    lines = simpleSplit(course_title, "Montserrat-Bold" if has_custom_fonts else "Helvetica-Bold", 24, width - 160)
    text_y = cy - 110
    for line in lines:
        c.drawCentredString(cx, text_y, line)
        text_y -= 110

    c.setStrokeColor(COLOR_DARK)
    c.setLineWidth(1.5)
    c.line(cx - 100, 80, cx + 100, 80)

    c.setFont("Montserrat" if has_custom_fonts else "Helvetica", 11)
    c.setFillColor(COLOR_DARK)
    c.drawCentredString(cx, 60, "SmartStudy Instructor")

    c.setFont("Montserrat-Bold" if has_custom_fonts else "Helvetica-Bold", 9)
    c.setFillColor(COLOR_GREY)
    date_str = certificate.issued_at.strftime('%B %d, %Y')
    c.drawString(50, 60, f"Date: {date_str}")
    c.drawRightString(width - 50, 60, f"Certificate ID: {certificate.certificate_id}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def wrap_text_intelligently(text, font, draw, max_width):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def _generate_png_sync(certificate):
    ensure_assets_exist()

    target_size = (3508, 2480)

    try:
        image = Image.open(BG_IMAGE_PATH).convert('RGB')
        if image.size != target_size:
            image = image.resize(target_size, Image.Resampling.LANCZOS)
    except:
        image = Image.new('RGB', target_size, color='white')
        draw_temp = ImageDraw.Draw(image)
        draw_decorative_border_png(draw_temp, target_size[0], target_size[1])

    width, height = image.size
    cx = width / 2
    cy = height / 2

    scale = width / 842

    logo_path_png = os.path.join(ASSETS_DIR, 'img', 'logo.png')
    logo_path_svg = os.path.join(ASSETS_DIR, 'img', 'logo.svg')

    logo = None

    if os.path.exists(logo_path_png):
        try:
            logo = Image.open(logo_path_png).convert('RGBA')
        except Exception as e:
            print(f"Error adding PNG logo: {e}")

    elif os.path.exists(logo_path_svg):
        try:
            import cairosvg
            png_data = cairosvg.svg2png(url=logo_path_svg, output_width=int(150 * scale),
                                        output_height=int(150 * scale))
            logo = Image.open(io.BytesIO(png_data)).convert('RGBA')
        except Exception as e:
            print(f"Error adding SVG logo: {e}")

    if logo:
        try:
            target_w = int(40 * scale)
            aspect = logo.height / logo.width
            target_h = int(target_w * aspect)

            logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

            logo_w, logo_h = logo.size
            image.paste(logo, (int(cx - logo_w / 2), 190), logo)
        except Exception as e:
            print(f"Error pasting logo: {e}")

    if HAS_QRCODE:
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
            qr.add_data(f"https://smartstudy.com/verify/{certificate.certificate_id}")  # TODO реалізувати перевірку сертифікату по QR коду
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200), Image.Resampling.LANCZOS)
            image.paste(qr_img, (width - 350, 150))
        except:
            pass

    draw = ImageDraw.Draw(image)

    FILL_DARK = COLOR_DARK_HEX
    FILL_GOLD = COLOR_GOLD_HEX
    FILL_GREY = COLOR_GREY_HEX

    font_main_title = get_pil_font("Montserrat-Bold", int(48 * scale))
    font_subtitle = get_pil_font("Montserrat-Regular", int(18 * scale))
    font_certify = get_pil_font("Montserrat-Regular", int(13 * scale))
    font_name = get_pil_font("GreatVibes-Regular", int(60 * scale))
    font_desc = get_pil_font("Montserrat-Regular", int(14 * scale))
    font_course = get_pil_font("Montserrat-Bold", int(24 * scale))
    font_footer = get_pil_font("Montserrat-Regular", int(11 * scale))
    font_footer_bold = get_pil_font("Montserrat-Bold", int(9 * scale))

    def draw_centered(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) / 2, y), text, font=font, fill=fill)

    draw_centered(int(100 * scale), "CERTIFICATE", font_main_title, FILL_DARK)

    draw_centered(int(170 * scale), "OF COMPLETION", font_subtitle, FILL_GOLD)

    line_y = int(200 * scale)
    draw.line([(cx - 100 * scale, line_y), (cx + 100 * scale, line_y)], fill=FILL_GOLD, width=int(2 * scale))

    draw_centered(cy - int(70 * scale), "This is to certify that", font_certify, FILL_GREY)

    student_name = f"{certificate.user.name} {certificate.user.surname}"
    draw_centered(cy - int(50 * scale), student_name, font_name, FILL_DARK)

    name_line_y = cy + int(15 * scale)
    draw.line([(cx - 180 * scale, name_line_y), (cx + 180 * scale, name_line_y)],
              fill=FILL_GOLD, width=int(1.5 * scale))

    draw_centered(cy + int(50 * scale), "has successfully completed the course:", font_desc, FILL_GREY)

    course_title = certificate.course.title
    max_text_width = width - int(160 * scale)
    course_lines = wrap_text_intelligently(course_title, font_course, draw, max_text_width)

    text_y = cy + int(90 * scale)
    for line in course_lines:
        draw_centered(text_y, line, font_course, FILL_DARK)
        text_y += int(30 * scale)

    footer_y = height - int(70 * scale)

    sig_line_y = height - int(80 * scale)
    draw.line([(cx - 100 * scale, sig_line_y), (cx + 100 * scale, sig_line_y)],
              fill=FILL_DARK, width=int(1.5 * scale))

    draw_centered(footer_y, "SmartStudy Instructor", font_footer, FILL_DARK)

    date_str = certificate.issued_at.strftime('%B %d, %Y')
    draw.text((int(50 * scale), footer_y), f"Date: {date_str}", font=font_footer_bold, fill=FILL_GREY)

    id_text = f"Certificate ID: {certificate.certificate_id}"
    bbox_id = draw.textbbox((0, 0), id_text, font=font_footer_bold)
    id_w = bbox_id[2] - bbox_id[0]
    draw.text((width - int(50 * scale) - id_w, footer_y), id_text, font=font_footer_bold, fill=FILL_GREY)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", quality=95, optimize=True)
    buffer.seek(0)
    return buffer


async def generate_certificate_file(certificate, fmt='pdf'):
    if fmt == 'pdf':
        return await sync_to_async(_generate_pdf_sync)(certificate)
    elif fmt == 'png':
        return await sync_to_async(_generate_png_sync)(certificate)
    return None
