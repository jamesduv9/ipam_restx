from ipaddress import IPv4Network
from sqlalchemy import types


class IPNetworkType(types.TypeDecorator):
    """
    Custom sqlalchemy type for ipv4 networks, allowing storage of ipaddress.IPv4Network objects
    """

    impl = types.Unicode

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, IPv4Network):
                try:
                    value = IPv4Network(value)
                except ValueError:
                    raise ValueError(f"Invalid IPv4 network: {value}")
            return str(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return IPv4Network(value)
            except ValueError:
                raise ValueError(
                    f"Invalid IPv4 network string in database: {value}")
        return None
