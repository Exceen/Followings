#!/usr/bin/python
# (c) 2013 Exceen

import tweepy
from os.path import exists

auth = tweepy.OAuthHandler('Consumer key', 'Consumer secret')
auth.set_access_token('Access token', 'Access token secret')
api = tweepy.API(auth)

def main():
  followers = api.followers_ids()
	print 'You have currently %d followers.' % len(followers)

	if exists('followers.txt'):

		recent_followers = [line.strip() for line in open('followers.txt')]

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
		
	writeFollowersToFile(followers)

def writeFollowersToFile(followers_list):
	followers_file = open('followers.txt', 'w')
	for user in followers_list:
		followers_file.write('%d\n' % user)
	followers_file.close()

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