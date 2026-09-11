import re


# ==================================================
# METADATA PARSER
# ==================================================

def parse_metadata(filename):

    original = filename

    # --------------------------------------------------
    # REMOVE FILE EXTENSION
    # --------------------------------------------------

    name = re.sub(
        r"\.(mkv|mp4|avi|mov|webm|m4v|ts)$",
        "",
        filename,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------
    # REMOVE UPLOADER PREFIX FIRST
    # Example:
    # @Team_XHPT - In the Grey
    #       ↓
    # In the Grey
    # --------------------------------------------------

    name = re.sub(
        r"^@[^-]+-\s*",
        "",
        name
    )

    # --------------------------------------------------
    # NORMALIZE SEPARATORS
    # --------------------------------------------------

    name = name.replace("_", " ")
    name = name.replace(".", " ")
    name = name.replace("-", " ")

    name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    # --------------------------------------------------
    # YEAR
    # --------------------------------------------------

    year_match = re.search(
        r"\b(19\d{2}|20\d{2})\b",
        name
    )

    year = None

    if year_match:
        year = int(year_match.group(1))

    # --------------------------------------------------
    # SEASON / EPISODE
    # --------------------------------------------------

    season = None
    episode = None

    series_match = re.search(
        r"\bS(\d{1,3})\s*E(\d{1,3})\b",
        name,
        flags=re.IGNORECASE
    )

    if series_match:

        season = int(series_match.group(1))
        episode = int(series_match.group(2))

    else:

        season_match = re.search(
            r"\bS(?:EASON)?\s*(\d{1,3})\b",
            name,
            flags=re.IGNORECASE
        )

        if season_match:

            season = int(
                season_match.group(1)
            )

    # --------------------------------------------------
    # QUALITY
    # --------------------------------------------------

    quality = None

    quality_patterns = [

        (r"\b2160p\b", "2160P"),
        (r"\b4K\b", "4K"),

        (r"\b1080p\b", "1080P"),
        (r"\b1080\b", "1080P"),
        (r"\bFHD\b", "1080P"),

        (r"\b720p\b", "720P"),
        (r"\b720\b", "720P"),
        (r"\bHD\b", "720P"),

        (r"\b480p\b", "480P"),
        (r"\b480\b", "480P"),
        (r"\bSD\b", "480P"),

        (r"\b360p\b", "360P"),
        (r"\b360\b", "360P"),
    ]

    for pattern, value in quality_patterns:

        if re.search(
            pattern,
            name,
            flags=re.IGNORECASE
        ):

            quality = value
            break

    # --------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------

    language = ""

    language_patterns = [

        (r"\bTamil\b", "Tamil"),
        (r"\bEnglish\b", "English"),
        (r"\bHindi\b", "Hindi"),
        (r"\bTelugu\b", "Telugu"),
        (r"\bMalayalam\b", "Malayalam"),
        (r"\bKannada\b", "Kannada"),
        (r"\bBengali\b", "Bengali"),
        (r"\bMarathi\b", "Marathi"),
        (r"\bPunjabi\b", "Punjabi"),
        (r"\bGujarati\b", "Gujarati"),
        (r"\bKorean\b", "Korean"),
        (r"\bJapanese\b", "Japanese"),
        (r"\bChinese\b", "Chinese"),
        (r"\bFrench\b", "French"),
        (r"\bSpanish\b", "Spanish"),
        (r"\bGerman\b", "German"),
    ]

    for pattern, value in language_patterns:

        if re.search(
            pattern,
            name,
            flags=re.IGNORECASE
        ):

            language = value
            break

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    title = name

    # --------------------------------------------------
    # REMOVE YEAR
    # --------------------------------------------------

    title = re.sub(
        r"\b(19\d{2}|20\d{2})\b",
        "",
        title
    )

    # --------------------------------------------------
    # REMOVE QUALITY
    # --------------------------------------------------

    for pattern, value in quality_patterns:

        title = re.sub(
            pattern,
            "",
            title,
            flags=re.IGNORECASE
        )

    # --------------------------------------------------
    # REMOVE LANGUAGE
    # --------------------------------------------------

    for pattern, value in language_patterns:

        title = re.sub(
            pattern,
            "",
            title,
            flags=re.IGNORECASE
        )

    # --------------------------------------------------
    # REMOVE COMMON TECHNICAL TAGS
    # --------------------------------------------------

    technical_tags = [

        "WEB-DL",
        "WEB DL",
        "WEBRip",
        "WEB Rip",
        "BluRay",
        "Blu Ray",
        "BRRip",
        "BR-Rip",
        "BDRip",
        "HDRip",
        "DVDRip",
        "HDTV",

        "HEVC",
        "H264",
        "H265",
        "x264",
        "x265",

        "AAC",
        "DDP",
        "DD",
        "5.1",
        "2.0",

        "TRUE",
        "PROPER",
        "REMASTERED",
        "UNCUT",
        "DUAL",
        "MULTI",

        "HQ",
        "Rip",
        "Rip",
    ]

    for tag in technical_tags:

        title = re.sub(
            rf"\b{re.escape(tag)}\b",
            "",
            title,
            flags=re.IGNORECASE
        )

    # --------------------------------------------------
    # REMOVE SERIES MARKERS
    # --------------------------------------------------

    title = re.sub(
        r"\bS\d{1,3}E\d{1,3}\b",
        "",
        title,
        flags=re.IGNORECASE
    )

    title = re.sub(
        r"\bS(?:EASON)?\s*\d{1,3}\b",
        "",
        title,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------
    # CLEAN TITLE
    # --------------------------------------------------

    title = re.sub(
        r"[()\[\]{}]",
        " ",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    title = title.strip(
        " -_."
    )

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    if not title:

        title = original

        title = re.sub(
            r"\.[^.]+$",
            "",
            title
        )

        title = title.strip()

    # --------------------------------------------------
    # RETURN
    # --------------------------------------------------

    return {
        "title": title,
        "year": year,
        "language": language,
        "quality": quality,
        "season": season,
        "episode": episode
    }