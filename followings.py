#!/usr/bin/python
# (c) 2015 Exceen
import tweepy
import argparse
from os import makedirs, path

consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
access_token = 'access_token'
access_token_secret = 'access_token_secret'

class TwitterAccount(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

        self.username = None
        self.friends = None
        self.followers = None

    def get_username(self):
        if self.username == None:
            self.username = self.api.me().screen_name
        return self.username

    def get_friends(self):
        if self.friends == None:
            self.friends = [str(friend) for friend in self.api.friends_ids(self.get_username())]
        return self.friends

    def get_followers(self):
        if self.followers == None:
            self.followers = [str(follower) for follower in self.api.followers_ids(self.get_username())]
        return self.followers

class Followings(object):

    def __init__(self, account):
        self.account = account
        self.workpath = path.join(path.dirname(path.realpath(__file__)), 'data')
        self.database_file = path.join(self.workpath, 'followers.db')
        self.friends_file = path.join(self.workpath, self.account.get_username() + '_friends')
        self.followers_file = path.join(self.workpath, self.account.get_username() + '_followers')

        if not path.exists(self.workpath):
            makedirs(self.workpath)

        self.friends_from_db = None
        self.followers_from_db = None
        
    def get_username_from_database(self, user_id):
        db = []
        if path.exists(self.database_file):
            db = [line.strip() for line in open(self.database_file, 'r')]
        for record in db:
            if str(user_id) in record:
                return record.split('|')[-1]
        return None

    def get_friends_from_database(self):
        if self.friends_from_db == None:
            if path.exists(self.friends_file):
                self.friends_from_db = [line.strip() for line in open(self.friends_file)]
            else:
                self.friends_from_db = self.account.get_friends()
        return self.friends_from_db

    def get_followers_from_database(self):
        if self.followers_from_db == None:
            if path.exists(self.followers_file):
                self.followers_from_db = [line.strip() for line in open(self.followers_file)]
            else:
                self.followers_from_db = self.account.get_followers()
        return self.followers_from_db

    def update_database(self, user_id_list):
        db = []
        if path.exists(self.database_file):
            db = [line.strip() for line in open(self.database_file, 'r')]

        user_id_list.append(self.account.get_username())
        for user_id in user_id_list:
            user_id = str(user_id)
            if not any(user_id in data for data in db):
                try:
                    data_set = user_id + '|' + str(self.account.api.get_user(user_id).screen_name)
                    db.append(data_set)
                except tweepy.error.TweepError, err:
                    continue

        with open(self.database_file, 'w') as f:
            [f.write('%s\n' % item) for item in db]

    def save_followings(self):
        with open(self.friends_file, 'w') as f:
            [f.write('%s\n' % item) for item in self.account.get_friends()]
        with open(self.followers_file, 'w') as f:
            [f.write('%s\n' % item) for item in self.account.get_followers()]
        self.update_database(self.account.get_friends() + self.account.get_followers())

def main():
    parser = argparse.ArgumentParser(description='Followings')
    parser.add_argument('-d', '--create-db', action='store_true', help='creates a complete database of your followers (ratelimit)')
    parser.add_argument('user', metavar='username', type=str, nargs='?', help='use the given username instead of yours')
    args = parser.parse_args()

    account = TwitterAccount(consumer_key, consumer_secret, access_token, access_token_secret)
    if args.user and account.get_username() != args.user:
        account.username = args.user

    followings = Followings(account)
    if args.create_db:
        followings.update_database(followings.account.get_friends() + followings.account.get_followers())
        exit()

    ####

    current_friends = followings.account.get_friends()
    current_followers = followings.account.get_followers()
    previous_friends = followings.get_friends_from_database()
    previous_followers = followings.get_followers_from_database()

    unfollowed_friends = list(set(previous_friends) - set(current_friends))
    new_friends = list(set(current_friends) - set(previous_friends))
    unfollowers = list(set(previous_followers) - set(current_followers))
    new_followers = list(set(current_followers) - set(previous_followers))

    followings.save_followings()

    ####

    print '@' + account.get_username(), '| Following:', len(followings.account.get_friends()), '| Followers:', len(followings.account.get_followers())

    print '\nUnfollowers(%d):' % len(unfollowers)
    print '\n'.join([followings.get_username_from_database(user_id) for user_id in unfollowers])

    print '\nNew Followers(%d):' % len(new_followers)
    print '\n'.join([followings.get_username_from_database(user_id) for user_id in new_followers])

    print '\nUnfollowed Friends(%d):' % len(unfollowed_friends)
    print '\n'.join([followings.get_username_from_database(user_id) for user_id in unfollowed_friends])

    print '\nNew Friends(%d):' % len(new_friends)
    print '\n'.join([followings.get_username_from_database(user_id) for user_id in new_friends])

    print ''


if __name__ == '__main__':
    main()
