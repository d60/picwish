from enum import Enum


class OCRLanguage(str, Enum):
    DEFAULT = 'ChinesePRC,English,Digits'
    DIGITS = 'Digits'
    ENGLISH = 'English'
    CHINESE_PRC = 'ChinesePRC'
    CHINESE_TAIWAN = 'ChineseTaiwan'
    FRENCH = 'French'
    GERMAN = 'German'
    JAPANESE = 'Japanese'
    PORTUGUESE = 'Portuguese'
    SPANISH = 'Spanish'
    ITALIAN = 'Italian'
    BULGARIAN = 'Bulgarian'
    CROATIAN = 'Croatian'
    CZECH = 'Czech'
    DANISH = 'Danish'
    DUTCH = 'Dutch'
    FINNISH = 'Finnish'
    GREEK = 'Greek'
    HUNGARIAN = 'Hungarian'
    KOREAN = 'Korean'
    NORWEGIAN = 'Norwegian'
    POLISH = 'Polish'
    RUSSIAN = 'Russian'
    SLOVENIAN = 'Slovenian'
    SWEDISH = 'Swedish'
    TURKISH = 'Turkish'


class OCRFormat(str, Enum):
    PDF = 'pdf'
    DOCX = 'docx'
    PPTX = 'pptx'
    XLSX = 'xlsx'
    TXT = 'txt'


class T2IQuality(int, Enum):
    LOW = 0
    HIGH = 1


class T2ITheme(int, Enum):
    GENERAL = 0
    DIGITAL_ART = 1
    _3D = 2
    PHOTOGRAPHY = 3
    ANIME = 4
    CYBERPUNK = 5
    PAINTING = 6
    PIXEL_ART = 7
    ILLUSTRATION = 8
    SKETCH = 9


class T2ISize(tuple, Enum):
    HD_1_1 = (616, 616)
    HD_3_2 = (768, 512)
    HD_4_3 = (704, 528)
    HD_3_4 = (528, 704)
    HD_16_9 = (904, 512)
    HD_9_16 = (512, 904)
    FHD_1_1 = (1024, 1024)
    FHD_3_2 = (1008, 672)
    FHD_4_3 = (1024, 768)
    FHD_3_4 = (768, 1024)
    FHD_16_9 = (1024, 576)
    FHD_9_16 = (576, 1024)
