import random, string, datetime
from PIL import Image, ImageOps

def get_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def format_date(timestamp: datetime.datetime) -> str:
    date = timestamp.date()
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    week_ago = today - datetime.timedelta(days=7)

    if date == today:
        return timestamp.strftime('%H:%M')
    elif date == yesterday:
        return 'Yesterday'
    elif date >= week_ago:
        return timestamp.strftime('%A')
    elif date.year == today.year:
        return timestamp.strftime('%d %b')
    else:
        return timestamp.strftime('%d %b %Y')

def resize_image(image: Image, size: int) -> Image:
    width, height = image.size
    min_dim = min(image.size)
    square_image = image.crop((
        (width - min_dim) // 2,
        (height - min_dim) // 2,
        (width + min_dim) // 2,
        (height + min_dim) // 2
    ))
    return square_image.resize((size, size))