import os
from PIL import Image, ImageDraw, ImageFont
def cert(media_root, nama: str, mata_pelajaran: str, date: str, no_cert: str, request)->str:
    dir = os.getcwd()
    template_generator = os.path.join(dir, 'cert_generator')

    img = Image.open(f'{template_generator}/cert_template/certificate_template.png')
    image_draw = ImageDraw.Draw(img)
    font_nama = ImageFont.truetype(f"{template_generator}/font/LeagueSpartan-Bold.ttf", 120)
    font_matapelajaran = ImageFont.truetype(f"{template_generator}/font/LeagueSpartan-Bold.ttf", 50)
    font_regular = ImageFont.truetype(f"{template_generator}/font/LeagueSpartan-Regular.ttf", 29)
    font_regular1 = ImageFont.truetype(f"{template_generator}/font/LeagueSpartan-Regular.ttf", 24)

    # Menghitung ukuran teks dan menempatkannya di tengah

    # Nama
    bbox = image_draw.textbbox((0, 0), nama.title().upper(), font=font_nama)
    text_width = bbox[2] - bbox[0]
    image_width, image_height = img.size
    x_position = (image_width - text_width) // 2
    image_draw.text((x_position, 690), nama.title().upper(), font=font_nama, fill=(0, 0, 0))

    # Mata pelajaran
    bbox = image_draw.textbbox((0, 0), mata_pelajaran.title().upper(), font=font_matapelajaran)
    text_width = bbox[2] - bbox[0]
    x_position = (image_width - text_width) // 2
    image_draw.text((x_position, 580), mata_pelajaran.title().upper(), font=font_matapelajaran, fill=(0, 0, 0))

    # Tanggal (di tempat yang sama seperti sebelumnya)
    image_draw.text((230, 62), date, font=font_regular, fill=(0, 0, 0))

    # No certi (di tempat yang sama seperti sebelumnya)
    image_draw.text((690, 62), no_cert, font=font_regular, fill=(0, 0, 0))

    # URL (di tempat yang sama seperti sebelumnya)
    url=f"{request.META['HTTP_HOST']}/media/sertifikat/{no_cert}.png"
    image_draw.text((1028, 1328), url, font=font_regular1, fill=(0, 0, 0))

    media_root = os.path.join(media_root, "sertifikat")
    if not os.path.exists(media_root):
        os.makedirs(media_root)

    cert_path = os.path.join(media_root, f"{no_cert}.png")
    img.save(cert_path)
    return  no_cert
