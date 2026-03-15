import ipaddress

class IpAddressValidation :

    def validation(self, ip ) -> bool:

        try:
            return ipaddress.ip_address(ip).is_private
        except ValueError:
            raise
        