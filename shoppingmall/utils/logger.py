from shoppingmall.models import Logs


class Logger:
    log: Logs

    def __init__(self):
        self.log = Logs()

    def set_request_size(self, request_size):
        self.log.request_size = request_size

    def set_response_size(self, response_size):
        self.log.response_size = response_size

    def set_status_code(self, status_code):
        self.log.status_code = status_code

    def set_server_type(self, server_type):
        self.log.server_type = server_type

    def set_method(self, method):
        self.log.method = method

    def set_path(self, path):
        self.log.path = path

    def set_data_string(self, data_string):
        self.log.data_string = data_string

    def set_payload_string(self, payload_string):
        self.log.payload_string = payload_string

    def set_shop_id(self, shop_id):
        self.log.shop_id = shop_id

    def set_user_id(self, user_id):
        self.log.user_id = user_id

    def request(self, data, method, path, shop_id, user_id):
        self.set_data_string(str(data))
        self.set_method(method)
        self.set_path(path)
        self.set_shop_id(shop_id)
        self.set_user_id(user_id)

    def response(self, data, status_code):
        self.set_payload_string(str(data))
        self.set_status_code(status_code)

    def d(self, data_string, method, path, shop_id, user_id, payload_string, status_code):
        self.set_data_string(str(data_string))
        self.set_method(method)
        self.set_path(path)
        self.set_shop_id(shop_id)
        self.set_user_id(user_id)
        self.set_payload_string(str(payload_string))
        self.set_status_code(status_code)
        self.save()

    def save(self):
        self.log.save()
