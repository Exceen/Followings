#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2014 Exceen

import tweepy
import argparse, logging
import os, sys
from os.path import exists

consumer_key = 'Consumer key'
consumer_secret = 'Consumer secret'
access_token = 'Access token'
access_token_secret = 'Acces token secret'

def main():

    followers_file_name = 'followers.txt'
    database_file_name = 'followers.db'

    script_path = sys.path[0] + '/'

    parser = argparse.ArgumentParser(description='Followings')
    parser.add_argument('-d', '--create-db', action='store_true', help='creates a complete database of your followers')
    parser.add_argument('-f', '--followers', action='store_true', help='lists all followers')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('user', metavar='username', type=str, nargs='?', help='use the given username instead of yours')
    args = parser.parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='[%(asctime)s] %(message)s', datefmt='%I:%M:%S %p')

    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        user = api.me().screen_name

        logging.debug('Authentication successful (logged in as @%s)' % user)
    except tweepy.error.TweepError, err:
        print err.reason[0]
        if 'invalid oauth token' in err.reason:
            print 'Please check you consumer and access keys!'
        logging.debug(err.reason)
        exit()

    followers_file = script_path + followers_file_name
    database_file = script_path + database_file_name
    if args.user:
        if user != args.user:
            user = api.get_user(args.user).screen_name
            followers_file = script_path + user + '_' + followers_file_name
        else:
            args.user = False

    try:
        followers = api.followers_ids(user)
        logging.debug('Follower ids of @%s loaded' % user)
    except tweepy.error.TweepError, err:
        print err.reason
        logging.debug(err.reason)
        exit()

    if args.create_db:
        update_database(followers, api, database_file)
        exit()

    print '%s currently %d followers.' % ('@' + user + ' has' if args.user else 'You have', len(followers))

    if args.followers:
        print_users(followers, api, database_file)
        exit()

    if exists(followers_file):
        recent_followers = [line.strip() for line in open(followers_file)]
        current_followers = [str(user) for user in followers]

        unfollowers = list(set(recent_followers) - set(current_followers))
        logging.debug('Determined unfollwers')
        new_followers = list(set(current_followers) - set(recent_followers))
        logging.debug('Determined new followers')

        print '\nunfollowers:'
        print_users(unfollowers, api, database_file)

        print '\nnew followers:'
        print_users(new_followers, api, database_file)

        if len(new_followers):
            update_database(new_followers, api, database_file)

        print '\n\nYou lost %d follower%s and got %d new follower%s.' % (len(unfollowers), '' if len(unfollowers) == 1 else 's', len(new_followers), '' if len(unfollowers) == 1 else 's')
    else:
        print 'I\'ll just create a file so that I have something to compare when you check your followings next time.'

    write_followers_to_file(followers, followers_file)
    logging.debug('Created new followers file')

def write_followers_to_file(followers_list, followers_file):
    with open(followers_file, 'w') as f:
        [f.write('%d\n' % user) for user in followers_list]

def print_users(user_id_list, api, database_file):
    if len(user_id_list) == 0:
        print 'none'
        logging.debug('Tried to print user id list but was empty')
    else:
        for user_id in user_id_list:
            try:
                user = api.get_user(user_id)
                print '%s (@%s)' % (user.name, user.screen_name)
            except tweepy.error.TweepError, err:
                err = err[0][0]
                print '%s (%s), user_id: %s, username: %s' % (err['message'], err['code'], user_id, get_username_from_database(user_id, database_file))
                logging.debug('user_id \'%s\' was not found' % user_id)
        logging.debug('Printed user id list')

def update_database(followers, api, database_file):
    followers.append(api.me().id)
    if os.path.exists(database_file):
        db = [line.strip() for line in open(database_file, 'r')]
        logging.debug('Opened existing database')
    else:
        db = []
        logging.debug('Created new database')

    if len(followers) > 0:
        for user_id in followers:
            user_id = str(user_id)
            contained = False
            for data in db:
                if user_id in data:
                    contained = True
                    logging.debug(user_id + ' already exists')
                    break

            if not contained:
                try:
                    user = api.get_user(user_id)
                    data_set = user_id + '|' + str(user.screen_name)
                    db.append(data_set)
                    logging.debug(user_id + ' (' + str(user.screen_name) + ')' + ' added to database')
                except tweepy.error.TweepError, err:
                    logging.debug(str(err.reason) + ', user_id: ' + user_id)
                    continue

        with open(database_file, 'w') as db_file:
            for data_set in db:
                db_file.write(data_set)
                db_file.write('\n')
        logging.debug('Saved followers in database')

def get_username_from_database(user_id, database_file):
    try:
        db = [line.strip() for line in open(database_file, 'r')]
        for element in db:
            if str(user_id) in element:
                return element.split('|')[-1]
    except:
        print 'no database available to look up the username'
        logging.debug('no database available')
    logging.debug('no username found in database')
    return 'no username found'

if __name__ == '__main__':
    main()
