import re
from email.message import Message


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
    pattern = r"from\s+[^\s]+\s+\([^\)]+\s+\[([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\]"
    from_ips = re.findall(pattern, text)
    if from_ips:
        return from_ips[0]
    return None


def extract_links(text):
    pattern = r'https?://[^\s"]+'
    links = re.findall(pattern, text)
    if links:
        return links
    return []


def ignore_dirty_chars(text):
    return str(text).encode("utf-8", "ignore").decode("utf-8")


def parse_ioc_from_eml_headers(headers):
    parsed_data = {}
    for header, value in headers:
        value = str(value)
        if header == "Delivered-To" and extract_email(value):
            parsed_data["dst-email"] = extract_email(value)
        if header == "To" and extract_email(value):
            parsed_data["to-email"] = extract_email(value)
        if header == "From" and extract_email(value):
            parsed_data["src-email"] = extract_email(value)
        if header == "Subject":
            parsed_data["subject"] = ignore_dirty_chars(value)
        if (
            header == "Received-SPF"
            and "src-ip" not in parsed_data
            and extract_clientip(value)
        ):
            parsed_data["src-ip"] = extract_clientip(value)
        if (
            header == "Received"
            and "src-ip" not in parsed_data
            and extract_fromip(value)
        ):
            parsed_data["src-ip"] = extract_fromip(value)
    return parsed_data


def parse_ioc_from_eml_body(body):
    parsed_data = {}
    for link in extract_links(ignore_dirty_chars(body)):
        if "links" not in parsed_data:
            parsed_data["links"] = []
        if link not in parsed_data["links"]:
            parsed_data["links"].append(link)
    return parsed_data


def email_unpack(eml: Message, emails: list = None):
    """Unpack nested emails.

    Return a list of emails in terms of headers, content-type and attachments (payloads).
    """
    if not emails:
        emails = []

    if eml.is_multipart():
        headers = eml.items()
        payloads = []
        for eml_part in eml.walk():
            content_type = eml_part.get_content_type()
            if content_type.startswith("multipart/"):
                continue
            if content_type.startswith("message/"):
                for nested_email in eml_part.get_payload():
                    emails = email_unpack(nested_email, emails)

            payload = eml_part.get_payload(decode=True)
            if payload:
                payloads.append(
                    {
                        "content-type": eml_part.get_content_type(),
                        "payload": payload.decode(),
                    }
                )
        if payloads:
            emails.append(
                {
                    "headers": headers,
                    "payloads": payloads,
                }
            )
    else:
        headers = eml.items()
        payload = eml.get_payload(decode=True)
        if payload:
            emails.append(
                {
                    "headers": headers,
                    "payloads": [
                        {
                            "content-type": eml.get_content_type(),
                            "payload": payload.decode(),
                        }
                    ],
                }
            )
    return emails
