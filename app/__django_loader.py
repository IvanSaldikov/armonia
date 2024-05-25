def load_django():
    # CALL THIS FIRST!!! BEFORE RUNNING SOMETHING FROM DJANGO!
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
    import django
    django.setup()
