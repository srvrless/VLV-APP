





class Decorate:
    def __init__(self):
        return
    
    def refresh_decorator(self, func):
        def check_refresh_validation():
            func()
        return check_refresh_validation
    
    def access_decorator(self, func):
        def check_access_validation():
            func()
        return check_access_validation
    
    def token_service_decorator(self, func):
        def get_email_from_token():
            func()
        return get_email_from_token
    
    def open_file_decorator(self, func):
        def open_file():
            func()
        return open_file
    
    def write_file_decorator(self, func):
        def write_file():
            func()
        return write_file
    





