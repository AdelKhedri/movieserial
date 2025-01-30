class OtpCode:
    def __init__(self, request, number=None, code=None):
        self.session = request.session
        self.number = number or self.session.get('number')
        self.code = code or self.session.get('code')

    def save(self):
        self.session['number'] = self.number
        self.session['code'] = self.code
        self.session.modified = True

    def get_data(self):
        return self.session.get('number', None), self.session.get('code', None)

    def validate_code(self, new_code):
        number, code = self.get_data()
        if number and code == new_code:
            self.clean()
            return True
        else:
            return False

    def clean(self):
        self.session.pop('number', None)
        self.session.pop('code', None)
        self.session.modified = True