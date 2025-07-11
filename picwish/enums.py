from enum import Enum


class OCRLanguage(str, Enum):
    """
    Enum representing supported OCR languages.
    """
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
    """
    Enum representing supported OCR output formats.
    """
    PDF = 'pdf'
    DOCX = 'docx'
    PPTX = 'pptx'
    XLSX = 'xlsx'
    TXT = 'txt'


class T2IQuality(int, Enum):
    """
    Enum representing text-to-image generation quality levels.
    """
    LOW = 0
    HIGH = 1


class T2ITheme(int, Enum):
    """
    Enum representing themes for text-to-image generation.
    """
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
    _UNKNOWN = 10


class T2ISize(tuple, Enum):
    """
    Enum representing supported image sizes for text-to-image generation.
    HD = High Definition
    FHD = Full High Definition
    """
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


class TranslateTargetLanguage(str, Enum):
    AR = 'AR'
    BG = 'BG'
    CHS = 'CHS'
    CHT = 'CHT'
    CSY = 'CSY'
    DEU = 'DEU'
    ENG = 'ENG'
    ESP = 'ESP'
    FRA = 'FRA'
    HUN = 'HUN'
    ID = 'ID'
    ITA = 'ITA'
    JPN = 'JPN'
    JW = 'JW'
    KOR = 'KOR'
    MS = 'MS'
    MY = 'MY'
    NLD = 'NLD'
    PLK = 'PLK'
    PTB = 'PTB'
    ROM = 'ROM'
    RUS = 'RUS'
    TH = 'TH'
    TL = 'TL'
    TRK = 'TRK'
    VIN = 'VI'


class TranslateSourceLanguage(str, Enum):
    CHS = 'CHS'
    CHT = 'CHT'
    ENG = 'ENG'
    JPN = 'JPN'


class ImageTranslator(str, Enum):
    ALIYUN = 'aliyun'
    GOOGLE = 'google'
    PAPAGO = 'papago'
