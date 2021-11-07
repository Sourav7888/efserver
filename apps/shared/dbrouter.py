class DefaultRouter:
    """
    A default router to control all database operations on models.
    Exclude any app that has its own router in 'exclude'
    """

    # Exclude the unwanted apps model here and then create
    # A special router for that apps in its own directory
    exclude = ["weather_manager"]

    def db_for_read(self, model, **hints):

        if model._meta.app_label not in self.exclude:
            return "default"

    def db_for_write(self, model, **hints):

        if model._meta.app_label not in self.exclude:
            return "default"

    def allow_relation(self, obj1, obj2, **hints):

        if (
            obj1._meta.app_label not in self.exclude
            or obj2._meta.app_label not in self.exclude
        ):
            return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label not in self.exclude:
            return "default"
