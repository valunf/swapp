
class Config(object):
    FLASK_LISTEN_IP = "127.0.0.1"
    FLASK_LISTEN_PORT = 5000
    BACKEND_ADDR = "127.0.0.1"
    BACKEND_PORT = 3000
    DEBUG = False

    @property
    def BACKEND_URI(self):
        return f"http://{self.BACKEND_ADDR}:{self.BACKEND_PORT}"


class ProductionConfig(Config):
    FLASK_LISTEN_IP = "0.0.0.0"
    BACKEND_ADDR = "backend"


class DevelopmentConfig(Config):
    BACKEND_ADDR = "localhost"
    DEBUG = True

class TestingConfig(Config):
    FLASK_LISTEN_IP = "0.0.0.0"
    BACKEND_ADDR = "localhost"
    DEBUG = True
