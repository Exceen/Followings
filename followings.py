#!/usr/bin/python
import tweepy
import argparse
import os, sys
from os.path import exists

consumer_key = 'Consumer key'
consumer_secret = 'Consumer secret'
access_token = 'Access token'
access_token_secret = 'Acces token secret'

database_file = None
api = None

def main():
    global api
    global database_file

    args = create_arguments()
    api = login()
    user = api.me().screen_name

    if args.user and user != args.user:
        user = api.get_user(args.user).screen_name

    workpath = sys.path[0] + '/data/'
    database_file = workpath + 'followers.db'
    followers_file = workpath + user + '_' + 'followers.txt'
    followings_file = workpath + user + '_' + 'followings.txt'

    followed = api.friends_ids(user)
    followers = api.followers_ids(user)

    if args.create_db:
        update_database(followers + followed)
        exit()

    print '%s currently follow%s %d people and %s %d followers.' % ('@' + user if args.user else 'You', 's' if args.user else '', len(followed), 'has' if args.user else 'have', len(followers))

    check_f(followers, user, followers_file, 'unfollowers', 'new followers')
    check_f(followed, user, followings_file, 'unfollowed', 'newly followed')
    print ''
def create_arguments():
    parser = argparse.ArgumentParser(description='Followings')
    parser.add_argument('-d', '--create-db', action='store_true', help='creates a complete database of your followers; you probably need to call this a few times every few minutes')
    # parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('user', metavar='username', type=str, nargs='?', help='use the given username instead of yours')
    return parser.parse_args()
def login():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth) #api
def check_f(user_id_list, user, f_file, string1, string2):
    if exists(f_file):
        recent_f = [line.strip() for line in open(f_file)]
        current_f = [str(user) for user in user_id_list]

        un_f = list(set(recent_f) - set(current_f))
        new_f = list(set(current_f) - set(recent_f))
        un_f = [item for item in un_f if item] # to remove empty strings, no clue why there are empty strings in this list

        print '\n%s(%d):' % (string1, len(un_f))
        print_users(un_f)

        print '\n%s(%d):' % (string2, len(new_f))
        print_users(new_f)

        update_database(new_f)
        
    write_list_to_file(user_id_list, f_file)
def write_list_to_file(a_list, a_file):
    with open(a_file, 'w') as f:
        [f.write('%s\n' % item) for item in a_list]
def print_users(user_id_list):
    if len(user_id_list) > 0:
        for user_id in user_id_list:
            try:
                user = api.get_user(user_id)
                print '%s (@%s)' % (user.name, user.screen_name)
            except tweepy.error.TweepError, err:
                err = err[0][0]
                print '%s; user_id: %s, username: %s' % (err['message'], user_id, get_username_from_database(user_id))
    else:
        print 'none'
def update_database(user_id_list):
    db = []
    if os.path.exists(database_file):
        db = [line.strip() for line in open(database_file, 'r')]

    user_id_list.append(api.me().id)
    for user_id in user_id_list:
        user_id = str(user_id)
        if not any(user_id in data for data in db):
            try:
                data_set = user_id + '|' + str(api.get_user(user_id).screen_name)
                db.append(data_set)
            except tweepy.error.TweepError, err:
                continue
    write_list_to_file(db, database_file)
def get_username_from_database(user_id):
    if exists(database_file):
        db = [line.strip() for line in open(database_file, 'r')]
    else:
        return 'no database found'
    for element in db:
        if str(user_id) in element:
            return element.split('|')[-1]
    return 'no username found'

if __name__ == '__main__':
    main()
