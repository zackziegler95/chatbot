


class JFormat:
    """
        enables packing and unapcking of objects into and out of JSON-like strings
        of the form "{"jtype": "type_of_message", "fields": {"k1": "v1", ... "kn": "vn"}}"
        where the keys in fields depend on the jtype

        message types:
            "login_request"
            "login_response"
            "create_request"
            "create_response"
            "list_request"
            "list_response"
            "text_message"      (no response--just sends TMs)
            "inbox_check"       (no response--just sends TMs)
            "delete_request"    (no response?)
    """

    def __init__(self, jstring):
        # sets jtype: str and fields: Dict[str: str]
        self.jtype = None
        self.fields = None
        self.jtype, self.fields = self.fromjstring(jstring)

    def _tojstring(self, jtype, fields):
        # expects jtype: str and fields:dict[str:str]
        msg = {"""jtype""": jtype, """fields""": fields}
        return str(message)

    def _fromjstring(self, jstring):
        try:
            pass
            #TODO: implement and test

        except Exception as e:
            print('Error unpacking jstring: ' + jstring)
            print('Error: ' + e)
        return jtype, fields

    def make_text_message(sender, recipient, message):
        jtype = 'text_message'
        fields = {
            'sender': str(sender),
            'recipient': str(recipient),
            'message': str(message)
        }
        return self._tojstring(jtype, fields)

    def make_user_list_request(sender):
        jtype = 'list_request'
        fields = {
            'sender': str(sender)
        }
        return self._tojstring(jtype, fields)

    def make_inbox_check(sender):
        jtype = 'inbox_check'
        fields = {
            'sender': str(sender)
        }
        return self._tojstring(jtype, fields)

    def make_delete_request(sender):
        jtype = 'delete_request'
        fields = {
            'sender': str(sender)
        }
        return self._tojstring(jtype, fields)

    def make_create_request(username):
        jtype = 'create_request'
        fields = {
            'sender': str(sender),
            'username': str(username)
        }
        return self._tojstring(jtype, fields)

    def make_login_request(username):
        jtype = 'login_request'
        fields = {
            'sender': str(sender),
            'username': str(username)
        }
        return self._tojstring(jtype, fields)
