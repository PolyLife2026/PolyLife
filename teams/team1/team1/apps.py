from django.apps import AppConfig


class Team1Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "team1"

    def ready(self):
        import team1.signals