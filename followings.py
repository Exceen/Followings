#!/usr/bin/python
# (c) 2013 Exceen

import tweepy
import argparse, logging
import os
from os.path import exists

consumer_key = 'Consumer key'
consumer_secret = 'Consumer secret'
access_token = 'Access token'
access_token_secret = 'Acces token secret'

def main():
	followers_file = 'followers.txt'

	parser = argparse.ArgumentParser(description='Followings')
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('-f', '--followers', action='store_true', help='lists all followers')
	parser.add_argument('user', metavar='username', type=str, nargs='?', help='use the given username instead of yours')
	args = parser.parse_args()

	if args.verbose:
		level = logging.DEBUG if args.verbose else logging.INFO
		logging.basicConfig(filename = 'debug.log', filemode='a', level = level, format='[%(asctime)s] %(message)s', datefmt='%I:%M:%S %p')

	try:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)
		user = api.me().screen_name

		logging.debug('Authentication successful (logged in as @%s)' % user)
	except tweepy.error.TweepError, err:
		print err.reason
		if 'invalid oauth token' in err.reason:
			print 'Please check you consumer and access keys!'
		logging.debug(err.reason)
		exit()

	if args.user:
		if user != args.user:
			user = args.user
			followers_file = user + '_' + followers_file
		else:
			args.user = False

	try:
		followers = api.followers_ids(user)
		logging.debug('Follower ids loaded')
	except tweepy.error.TweepError, err:
		print err.reason
		logging.debug(err.reason)
		exit()

	print '%s currently %d followers.' % ('@' + user + ' has' if args.user else 'You have', len(followers))
	

	if args.followers:
		printUsers(followers, api)
		exit()

	if exists(followers_file):
		recent_followers = [line.strip() for line in open(followers_file)]
		current_followers = [str(user) for user in followers]

		unfollowers = list(set(recent_followers) - set(current_followers))
		logging.debug('Calculated unfollwers')
		new_followers = list(set(current_followers) - set(recent_followers))
		logging.debug('Calculated new followers')

		print '\nunfollowers:'
		printUsers(unfollowers, api)

		print '\nnew followers:'
		printUsers(new_followers, api)

		print '\n\nYou lost %d follower%s and got %d new follower%s.' % (len(unfollowers), '' if len(unfollowers) == 1 else 's', len(new_followers), '' if len(unfollowers) == 1 else 's')
	else:
		print 'I\'ll just create a file so that I have something to compare when you check your followings next time.'

	writeFollowersToFile(followers, followers_file)
	logging.debug('Created new followers file')

def writeFollowersToFile(followers_list, followers_file):
	with open(followers_file, 'w') as f:
		[f.write('%d\n' % user) for user in followers_list]

def printUsers(user_id_list, api):
	if len(user_id_list) == 0:
		print 'none'
		logging.debug('Tried to print user id list, but was empty')
	else:
		for user_id in user_id_list:
			try:
				user = api.get_user(user_id)
			except tweepy.error.TweepError, err:
				print err.reason
				logging.debug(err.reason)
				exit()
			print '%s (@%s)' % (user.name, user.screen_name)
		logging.debug('Printed user id list')

if __name__ == '__main__':
	main()



