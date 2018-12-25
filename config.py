import os


class Config(object):
    """Настройки фласк-приложения"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'