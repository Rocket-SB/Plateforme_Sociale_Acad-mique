"""
Django settings for config project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv('SECRET_KEY')



# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.getenv('DEBUG', 'False') == 'True'



ALLOWED_HOSTS = []

if DEBUG:

    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

else:

    # Make sure to set the ALLOWED_HOSTS environment variable in production

    # with a comma-separated list of your domains.

    ALLOWED_HOSTS.extend(os.getenv('ALLOWED_HOSTS', '').split(','))


# Application definition

INSTALLED_APPS = [

    'jazzmin',

    'daphne',

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.staticfiles',

    'channels',

    # Custom apps

    'apps.users',

    'apps.publications',

    'apps.groups',

    'apps.posts',

    'apps.messaging',

    'apps.comments',

    'apps.notifications',

    'simple_history',

    'apps.recommendations', 

]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.users.middleware.ActiveUserMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'simple_history.middleware.HistoryRequestMiddleware',

]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.debug',

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

                'apps.notifications.context_processors.notifications',



            ],



        },



    },



]


WSGI_APPLICATION = 'config.wsgi.application'

ASGI_APPLICATION = "config.asgi.application"



# Database



# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {

    'default': {

        'ENGINE': 'mysql.connector.django',

        'NAME': os.getenv('DB_NAME', 'research_platform'),

        'USER': os.getenv('DB_USER', 'root'),

        'PASSWORD': os.getenv('DB_PASSWORD'),

        'HOST': os.getenv('DB_HOST', 'localhost'),

        'PORT': os.getenv('DB_PORT', '3306'),

        'OPTIONS': {

            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",

            'charset': 'utf8mb4',

        },

    }


}


# MongoDB configuration (PyMongo direct - pas Djongo)



MONGODB_SETTINGS = {

    'host': os.getenv('MONGODB_HOST', 'localhost'),

    'port': int(os.getenv('MONGODB_PORT', 27017)),

    'database': os.getenv('MONGODB_DATABASE', 'research_platform_mongo'),

    'username': os.getenv('MONGODB_USER'),  

    'password': os.getenv('MONGODB_PASSWORD'), 


}



# Password validation



# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [



    {

        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },



    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },



    {

        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },


    {

        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',

    },



]


# Internationalization



# https://docs.djangoproject.com/en/5.0/ref/settings/#i18n



LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)



# https://docs.djangoproject.com/en/5.0/howto/static-files/


STATIC_URL = 'static/'

STATICFILES_DIRS = [

    BASE_DIR / 'static',

]



STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files



MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type



# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Custom User Model

AUTH_USER_MODEL = 'users.Utilisateur'



# Channels

if DEBUG:

    CHANNEL_LAYERS = {

        "default": {

            "BACKEND": "channels.layers.InMemoryChannelLayer",

        },

    }

else:

    CHANNEL_LAYERS = {

        "default": {

            "BACKEND": "channels_redis.core.RedisChannelLayer",

            "CONFIG": {

                "hosts": [(os.getenv('REDIS_HOST', '127.0.0.1'), os.getenv('REDIS_PORT', 6379))],

            },

        },

    }



# Security settings for production

if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True


JAZZMIN_SETTINGS = {
    "site_title": "MonProjet Admin",
    "site_header": "MonProjet",
    "site_brand": "MonProjet",
    "welcome_sign": "Welcome to MonProjet Admin",
    "copyright": "MonProjet Ltd.",
}


# Neo4j Configuration
NEO4J_SETTINGS = {
    'host': os.getenv('NEO4J_HOST', 'localhost'),
    'port': int(os.getenv('NEO4J_PORT', 7687)),
    'username': os.getenv('NEO4J_USER', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', 'password'),
    'database': os.getenv('NEO4J_DATABASE', 'neo4j'),
}

# Neo4j URI (bolt protocol for driver)
NEO4J_URI = f"bolt://{NEO4J_SETTINGS['host']}:{NEO4J_SETTINGS['port']}"