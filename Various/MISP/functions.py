import re

def extract_email(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(pattern, text)
    if emails:
        return emails[0].lower()
    return None


def extract_clientip(text):
    pattern = r"client-ip=([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"
    client_ips = re.findall(pattern, text)
    if client_ips:
        return client_ips[0]
    return None


def extract_fromip(text):
    pattern = r'from\s+[^\s]+\s+\([^\)]+\s+\[([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\]'
    from_ips = re.findall(pattern, text)
    if from_ips:
        return from_ips[0]
    return None


def extract_links(text):
    pattern = r'href="(https?://[^\s]+)"'
    links = re.findall(pattern, text)
    if links:
        return links
    return []
