import ipaddress
import socket
from urllib.parse import urlparse

MAX_RESPONSE_BYTES = 2_000_000
MAX_REDIRECTS = 5
CGNAT = ipaddress.ip_network("100.64.0.0/10")
METADATA_V4 = ipaddress.ip_address("169.254.169.254")


class UnsafeUrlError(ValueError):
    """Raised when a URL is not safe to fetch from this host."""


def is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if ip.version == 6 and ip.ipv4_mapped is not None:
        return is_blocked_ip(ip.ipv4_mapped)
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        return True
    if ip.version == 4 and (ip in CGNAT or ip == METADATA_V4):
        return True
    return False


def assert_public_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrlError("only http and https URLs are allowed")
    host = parsed.hostname
    if not host:
        raise UnsafeUrlError("URL is missing a host")
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if is_blocked_ip(literal):
            raise UnsafeUrlError("refusing to fetch a private or reserved address")
        return
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeUrlError(f"could not resolve host: {host}") from exc
    if not infos:
        raise UnsafeUrlError(f"could not resolve host: {host}")
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if is_blocked_ip(address):
            raise UnsafeUrlError("refusing to fetch a host that resolves to a private or reserved address")
