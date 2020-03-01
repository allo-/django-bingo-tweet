from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

import tweepy

from bingo.models import Game

TWITTER_API_KEY = getattr(settings, "TWITTER_API_KEY", None)
TWITTER_API_SECRET = getattr(settings, "TWITTER_API_SECRET", None)
TWITTER_ACCESS_TOKEN = getattr(settings, "TWITTER_ACCESS_TOKEN", None)
TWITTER_ACCESS_TOKEN_SECRET = getattr(
    settings,
    "TWITTER_ACCESS_TOKEN_SECRET", None)
TWEET_TEXT = getattr(settings, "TWEET_TEXT",
    _("New game: http://{domain:s}{absolute_url:s}"))
TWEET_TEXT_WITH_TOPIC = getattr(settings, "TWEET_TEXT_WITH_TOPIC",
    _("New game: http://{domain:s}{absolute_url:s} (Topic: {topic:s})"))


class TwitterAPIKey(models.Model):
    name = models.CharField(max_length=255, help_text="A name for the API key "
        "that allows you to distinguish it from other API keys.")
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class TwitterConfig(models.Model):
    site = models.OneToOneField(Site, unique=True)
    api_key = models.ForeignKey(TwitterAPIKey)
    tweet_text = models.CharField(max_length=255, default=_("New game: http://{domain:s}{absolute_url:s}"))
    tweet_text_with_topic = models.CharField(max_length=255, default=_("New game: http://{domain:s}{absolute_url:s} (Topic: {topic:s})"))


@receiver(post_save, sender=Game)
def tweet_game(sender, instance, created, **kwargs):
    game = instance
    try:
        config = TwitterConfig.objects.get(site=game.site)
        if game.description:
            tweet = config.tweet_text_with_topic.format(
                domain=game.site.domain,
                absolute_url=game.get_absolute_url(),
                topic=game.description)
        else:
            tweet = config.tweet_text.format(
                domain=game.site.domain,
                absolute_url=game.get_absolute_url())
        try:
            auth = tweepy.OAuthHandler(config.api_key.key, config.api_key.secret)
            auth.set_access_token(config.api_key.access_token,
                                  config.api_key.access_token_secret)
            api = tweepy.API(auth)
            api.update_status(status=tweet)
        except tweepy.TweepError:
            import logging
            logger = logging.getLogger("root")
            logger.error("Could not tweet game {game_id} on site {domain}. Check your twitter credentials and twitter API status.".format(game_id=game.game_id, domain=game.site.domain))
    except ObjectDoesNotExist:
        return
