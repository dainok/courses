import re
import quopri

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


def parse_eml(eml):
    email_data = {}
    for header, value in eml.items():
        if header == "Delivered-To" and extract_email(value):
            email_data["dst-email"] = extract_email(value)
        if header == "To" and extract_email(value):
            email_data["to-email"] = extract_email(value)
        if header == "From" and extract_email(value):
            email_data["src-email"] = extract_email(value)
        if header == "Subject":
            email_data["subject"] = value
        if header == "Received-SPF" and not "src-ip" in email_data and extract_clientip(value):
            email_data["src-ip"] = extract_clientip(value)
        if header == "Received" and not "src-ip" in email_data and extract_fromip(value):
            email_data["src-ip"] = extract_fromip(value)

    for eml_body in eml.get_payload():
        body = quopri.decodestring(str(eml_body)).decode("utf-8")
        for link in extract_links(body):
            if "links" not in email_data:
                email_data["links"] = []
            if link not in email_data["links"]:
                email_data["links"].append(link)
    return email_data
