import ipaddress

class IpAddressValidation :

    def validation(self, ip ) -> bool:
        try:
            return ipaddress.ip_address(ip[0]).is_private
        except ValueError:
            pass
        