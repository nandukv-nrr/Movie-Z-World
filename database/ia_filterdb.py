# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re, base64, json
from struct import pack
from pyrogram.file_id import FileId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from info import FILE_DB_URI, SEC_FILE_DB_URI, DATABASE_NAME, COLLECTION_NAME, MULTIPLE_DATABASE, USE_CAPTION_FILTER, MAX_B_TN

# First Database For File Saving 
client = MongoClient(FILE_DB_URI)
db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

# Second Database For File Saving
sec_client = MongoClient(SEC_FILE_DB_URI)
sec_db = sec_client[DATABASE_NAME]
sec_col = sec_db[COLLECTION_NAME]


async def save_file(media):
    """Save file in the database."""
    
    file_id = unpack_new_file_id(media.file_id)
    file_name = clean_file_name(media.file_name)
    
    file = {
        'file_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': media.caption.html if media.caption else None
    }

    if is_file_already_saved(file_id, file_name):
        return False, 0

    try:
        col.insert_one(file)
        print(f"{file_name} is successfully saved.")
        return True, 1
    except DuplicateKeyError:
        print(f"{file_name} is already saved.")
        return False, 0
    except:
        if MULTIPLE_DATABASE:
            try:
                sec_col.insert_one(file)
                print(f"{file_name} is successfully saved.")
                return True, 1
            except DuplicateKeyError:
                print(f"{file_name} is already saved.")
                return False, 0
        else:
            print("Your Current File Database Is Full, Turn On Multiple Database Feature And Add Second File Mongodb To Save File.")

def clean_file_name(file_name):
    """Clean and format the file name."""
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name)) 
    unwanted_chars = ['[', ']', '(', ')', '{', '}']
    
    for char in unwanted_chars:
        file_name = file_name.replace(char, '')
        
    return ' '.join(filter(lambda x: not x.startswith('@') and not x.startswith('http') and not x.startswith('www.') and not x.startswith('t.me'), file_name.split()))

def is_file_already_saved(file_id, file_name):
    """Check if the file is already saved in either collection."""
    found1 = {'file_name': file_name}
    found = {'file_id': file_id}

    for collection in [col, sec_col]:
        if collection.find_one(found1) or collection.find_one(found):
            print(f"{file_name} is already saved.")
            return True
            
    return False

def _normalize_media_name(file_name):
    text = str(file_name or "")
    text = re.sub(r"\.(mkv|mp4|avi|m4v|mov|wmv|flv|webm|ts)$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[_.,\-+]+", " ", text)
    text = re.sub(r"[\[\]\(\)\{\}]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()

def _extract_media_sort_key(file_name):
    normalized = _normalize_media_name(file_name)
    title = normalized
    season = -1
    episode = -1
    quality_rank = -1

    match = re.search(r"\bs(\d{1,2})\s*e(\d{1,3})\b", normalized, flags=re.IGNORECASE)
    if match:
        season = int(match.group(1))
        episode = int(match.group(2))
        title = re.sub(r"\bs\d{1,2}\s*e\d{1,3}\b", " ", title, flags=re.IGNORECASE)
    else:
        match = re.search(r"\bseason\s*(\d{1,2})\s*episode\s*(\d{1,3})\b", normalized, flags=re.IGNORECASE)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            title = re.sub(r"\bseason\s*\d{1,2}\s*episode\s*\d{1,3}\b", " ", title, flags=re.IGNORECASE)

    if season == -1:
        match = re.search(r"\bseason\s*(\d{1,2})\b", normalized, flags=re.IGNORECASE)
        if match:
            season = int(match.group(1))
            title = re.sub(r"\bseason\s*\d{1,2}\b", " ", title, flags=re.IGNORECASE)
        else:
            match = re.search(r"\bs(\d{1,2})\b", normalized, flags=re.IGNORECASE)
            if match:
                season = int(match.group(1))
                title = re.sub(r"\bs\d{1,2}\b", " ", title, flags=re.IGNORECASE)

    if episode == -1:
        match = re.search(r"\b(?:episode|ep)\s*(\d{1,3})\b", normalized, flags=re.IGNORECASE)
        if match:
            episode = int(match.group(1))
            title = re.sub(r"\b(?:episode|ep)\s*\d{1,3}\b", " ", title, flags=re.IGNORECASE)

    quality_match = re.search(r"\b(2160p|1080p|720p|480p|360p|4k)\b", normalized, flags=re.IGNORECASE)
    if quality_match:
        quality_text = quality_match.group(1).lower()
        quality_rank_map = {
            "4k": 4000,
            "2160p": 2160,
            "1080p": 1080,
            "720p": 720,
            "480p": 480,
            "360p": 360,
        }
        quality_rank = quality_rank_map.get(quality_text, -1)

    title = re.sub(r"\b(2160p|1080p|720p|480p|360p|4k|web[\s-]?dl|web[\s-]?rip|bluray|hdrip|hevc|x264|x265|aac|10bit)\b", " ", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip()

    has_series_meta = 0 if (season != -1 or episode != -1) else 1
    season_sort = season if season != -1 else 10**6
    episode_sort = episode if episode != -1 else 10**6
    quality_sort = -quality_rank if quality_rank != -1 else 0
    return (has_series_meta, title, season_sort, episode_sort, quality_sort, normalized)

def sort_search_results(files):
    return sorted(files, key=lambda item: _extract_media_sort_key(item.get("file_name")))

async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query
    filter = {'file_name': regex}
    files = []
    if MULTIPLE_DATABASE:
        cursor1 = col.find(filter)
        cursor2 = sec_col.find(filter)
        
        for file in cursor1:
            files.append(file)
        for file in cursor2:
            files.append(file)
    else:
        cursor = col.find(filter)
        
        for file in cursor:
            files.append(file)

    files = sort_search_results(files)
    files = files[offset:offset + max_results]
    total_results = col.count_documents(filter) if not MULTIPLE_DATABASE else (col.count_documents(filter) + sec_col.count_documents(filter))
    next_offset = "" if (offset + max_results) >= total_results else (offset + max_results)

    return files, next_offset, total_results

async def get_bad_files(query, file_type=None, use_filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = rf'(\b|[.+-_]){query}(\b|[.+-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[s.+-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return [], 0

    filter_criteria = {'file_name': regex}
    if USE_CAPTION_FILTER:
        filter_criteria = {'$or': [filter_criteria, {'caption': regex}]}

    def count_documents(collection):
        return collection.count_documents(filter_criteria)

    total_results = (count_documents(col) + count_documents(sec_col) if MULTIPLE_DATABASE else count_documents(col))

    def find_documents(collection):
        return list(collection.find(filter_criteria))

    files = (find_documents(col) + find_documents(sec_col) if MULTIPLE_DATABASE else find_documents(col))

    return files, total_results

async def get_file_details(query):
    return col.find_one({'file_id': query}) or sec_col.find_one({'file_id': query})

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")
    
def unpack_new_file_id(new_file_id):
    """Return file_id"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id
    
