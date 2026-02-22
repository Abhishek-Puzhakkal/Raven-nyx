import ipaddress

class IpAddressValidation :
    def __init__(self, private_ip : list):
        self.ip = private_ip[0]

    def validation(self) -> bool:

        try:

            return ipaddress.ip_address(self.ip).is_private
        except ValueError:
            pass
        