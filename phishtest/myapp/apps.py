from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        from actstream.registry import register
        from django.contrib.auth.models import User
        from .models import PhishingEmail
        register(User)
        register(PhishingEmail)
