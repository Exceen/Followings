Followings
==========

Followings makes it possible to see who (un)followed you and your friends on Twitter as well who you and your friends (un)followed.

usage: followings.py [-h] [-d] [username]

Before you are able to use this script you need to create a new Twitter-Application on https://dev.twitter.com/apps/new.
Create your Access-Keys and replace the 4 keys in the script with the ones from your Twitter-Application.

Tweepy is required to run this script:
https://github.com/tweepy/tweepy

AUTO Followings
===============

To use this one, you need to create a second Twitter account and add access keys for this account as well (dev_xxx). Add it as a cronjob and it will send a DM to your main account whenever there are some changes on your followers/followings.

