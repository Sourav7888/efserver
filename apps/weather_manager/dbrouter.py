class WeatherDataRouter:
    """
    A router to control all database operations on models in the
    weather data applications.
    """

    app_label = "weather_manager"

    def db_for_read(self, model, **hints):

        if model._meta.app_label == self.app_label:
            return "weatherdatadb"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label == app_label:
            return db == "weatherdatadb"
        return None
