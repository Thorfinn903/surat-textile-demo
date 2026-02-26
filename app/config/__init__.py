from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
