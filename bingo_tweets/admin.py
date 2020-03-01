from django.contrib import admin
from django.db import models
from .models import *

class TwitterAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("name",)

class TwitterConfigAdmin(admin.ModelAdmin):
    list_display = ("site", "api_key", "tweet_text", "tweet_text_with_topic")
    list_filter = ("site",)
    list_editable = ("api_key", "tweet_text", "tweet_text_with_topic")

admin.site.register(TwitterAPIKey, TwitterAPIKeyAdmin)
admin.site.register(TwitterConfig, TwitterConfigAdmin)
