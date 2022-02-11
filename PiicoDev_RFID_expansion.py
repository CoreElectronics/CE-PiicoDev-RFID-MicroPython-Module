from PiicoDev_RFID import PiicoDev_RFID_Base

class PiicoDev_RFID(PiicoDev_RFID_Base):
    def writeURL(self, uri): # Currently only supported by NTAG213
        is_ndef_message = chr(3)
        ndef_length = chr(len(url) + 5)
        ndef_record_header = chr(209)
        ndef_type_length = chr(1)
        ndef_payload_length = chr(len(url) + 1)
        is_uri_record = chr(85)
        record_type_indicator = chr(0)
        tlv_terminator = chr(254)
        ndef = is_ndef_message + ndef_length + ndef_record_header + ndef_type_length + ndef_payload_length + is_uri_record + record_type_indicator + uri + tlv_terminator
        print(ndef)
        success = self.writeText(ndef, ignore_null=True)
        return success
