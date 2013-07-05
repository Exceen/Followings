#!/usr/bin/python
# (c) 2013 Exceen

import tweepy
import argparse
from os.path import exists

try:
	auth = tweepy.OAuthHandler('Consumer key', 'Consumer secret')
	auth.set_access_token('Access token', 'Access token secret')
	api = tweepy.API(auth)
	api.me()
except tweepy.error.TweepError, err:
	print err.reason
	if 'invalid oauth token' in err.reason:
		print 'Please check you consumer and access keys!'
	exit()

def main():

	followers_file = 'followers'

	parser = argparse.ArgumentParser(description='Followings v1.1')
	parser.add_argument('-f', '--followers', action='store_true', help='lists all followers')
	parser.add_argument('user', metavar='username', type=str, nargs='?', help='use another username instead of yours')
	args = parser.parse_args()

	user = api.me().screen_name
	if args.user:
		user = args.user
		followers_file += '.' + user

	followers = api.followers_ids(user)
	print 'You have currently %d followers.' % len(followers)

	if args.followers:
		printUsers(followers)
		exit()


	if exists(followers_file):
		recent_followers = [line.strip() for line in open(followers_file)]

		current_followers = []
		for user in followers:
			current_followers.append(str(user))

		unfollowers = list(set(recent_followers) - set(current_followers))
		new_followers = list(set(current_followers) - set(recent_followers))

		print '\nunfollowers:'
		printUsers(unfollowers)

		print '\nnew followers:'
		printUsers(new_followers)

		print '\n\nYou lost %d follower%s and got %d new follower%s.' % (len(unfollowers), plural(len(unfollowers)), len(new_followers), plural(len(new_followers)))

	else:
		print 'I just created a file so that I have something to compare when you check your followings next time.'

	writeFollowersToFile(followers, followers_file)

def writeFollowersToFile(followers_list, followers_file):
	file_to_write = open(followers_file, 'w')
	for user in followers_list:
		file_to_write.write('%d\n' % user)
	file_to_write.close()

def printUsers(user_id_list):
	if len(user_id_list) == 0:
		print 'none'
	else:
		for user_id in user_id_list:
			user = api.get_user(user_id)
			print '%s (@%s)' % (user.name, user.screen_name)

def plural(n):
	if n == 1:
		return ''
	return 's'

if __name__ == '__main__':
	main()
