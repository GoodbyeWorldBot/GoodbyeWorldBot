#!/usr/bin/python

# Author: reddit.com/u/GoodbyeWorldBot aka GoodbyeWorldBot@gmail.com

# ver	dd/mm/yyyy	/u/whoever-did-change	detail
# v1.0	14/10/2012	/u/GoodbyeWorldBot	Initial version
# v1.1	15/10/2012	/u/GoodbyeWorldBot	Added better output, optional delete comments

import time
import praw
import socket
import pprint
import urllib2
import os
import argparse

version = "1.1"
version_token = "GoodbyeWorldBot_v" + version
user_agent = "/u/GoodbyeWorldBot v" + version + " by /r/GoodbyeWorld"
message = "The owner of this account has requested this content be removed by /u/GoodbyeWorldBot\n\nVisit /r/GoodbyeWorld for more information.\n\n" + version_token


parser = argparse.ArgumentParser(description="A script that automates the deletion of comments and submissions the supplied Reddit.com user.  Default behaviour is to change all comments and self-post-text to a \"goodbye\" message, and to delete all submissions.", epilog="See reddit.com/r/GoodbyeWorld and /u/GoodbyeWorld for support.")
# add options for the deletion notice.. --message ?
parser.add_argument("--show-message",			 action="store_true", default=False,	help="Print the goodbye message")
parser.add_argument("--dont-change-comments",	 action="store_true", default=False,	help="Do not change comments to the GoodbyeWorldBot deletion notice [default is to change]")
parser.add_argument("--delete-comments", 		 action="store_true", default=False,	help="Delete comments [default is to leave them]. Can be combined with --dont-edit-comments")
parser.add_argument("--dont-add-goodbye",		 action="store_true", default=False,	help="Do not add a comment to all submissions containing the goodbye message [default is to add a goodbye comment]")
parser.add_argument("--dont-change-submissions", action="store_true", default=False,	help="Do not change self-post-text to the GoodbyeWorldBot deletion notice [default is to change it]")
parser.add_argument("--dont-delete-submissions", action="store_true", default=False, 	help="Do not delete submissions. [default is to delete them]. Can be combined with --dont-change-submissions")
parser.add_argument("--dont-show-content",		 action="store_true", default=False,	help="Do not print the content of posts and submissions prior to modification [default]")
parser.add_argument("username", 				 										help="The Reddit.com username to act upon")
parser.add_argument("password", 				 										help="The password for the specified username")
args = parser.parse_args()


if args.show_message:
	print "Using the following message when editing self-posts and comments:"
	print "~~~~~~~~~~~~~~~~~~~~~~~~~"
	print message
	print "~~~~~~~~~~~~~~~~~~~~~~~~~"
	print
	raise SystemExit

try:
	result = None
	submissions = None
	comments = None

	print "+Logging in to Reddit using username '" + args.username + "'"
	r = praw.Reddit(user_agent=user_agent)
	r.login(username=args.username, password=args.password)
	user = r.get_redditor(args.username)
	print ":Logged in to Reddit"

	deleted_submissions = 0
	commented_submissions = 0
	edited_submissions = 0

	edited_comments = 0
	deleted_comments = 0

	submissions = user.get_submitted(limit=None)
	for submission in submissions:
		print "========================="
		print "Processing submission " + submission.short_link
		print submission.title.encode("utf-8")
		print "-------------------------"
	
		if submission.is_self and args.dont_show_content:
			pass
		else:
			# print the body
			print "+Submission self-post-text:"
			print "~~~~~~~~~~~~~~~~~~~~~~~~~"
			print submission.selftext.encode("utf-8")
			print "~~~~~~~~~~~~~~~~~~~~~~~~~"

		if submission.is_self and args.dont_change_submissions: 
			pass
		else:
			# Edit self-post text
			print "+Checking for '" + version_token + "' in body"
			if version_token in submission.selftext:
				print ":Self post text already constains version_token, not editing"
			else:
				result = submission.edit(message)
				if result == None:
					print ":FAILED to edit self-post text on submission"
				else:
					print ":Edited self-post text on submission"
					edited_submissions += 1
		
		if args.dont-add-goodbye:
			pass
		else:
			# Add a comment to the submission
			print "+Adding comment"
			result = submission.add_comment(message)
			if result == None:
				print ":FAILED to add comment to submission"
			else:
				print ":Added comment to submission"
				commented_submissions += 1
		
		if args.dont_delete_submissions:
				pass
		else:
			# Delete the submission
			print "+Attempting to delete submission"
			result = submission.delete()
			if result == None:
				print ":FAILED to delete submission"
			else:
				print ":Deleted submission"
				deleted_submissions += 1

		# done this submission
		print "+Processing complete for " + submission.short_link
		print

	# dumpt the submission results
	print "Submission Results:"
	print "Commented on " + str(commented_submissions) + " submissions"
	print "Edited self-post text on " + str(edited_submissions) + " submissions"
	print "Deleted " + str(commented_submissions) + " submissions"
	print
	print "Taking a 10s sleep so you can CTRL-C if needed"
	time.sleep(10)
	print "Moving on to comments then.."



	# On to the comments!
	comments = user.get_comments(limit=None)
	for comment in comments:
		print "========================="
		print comment.permalink
		print "-------------------------"

		if args.dont_show_content:
			pass
		else:
			print "Comment text:"
			print "~~~~~~~~~~~~~~~~~~~~~~~~~"
			print comment.body.encode("utf-8")
			print "~~~~~~~~~~~~~~~~~~~~~~~~~"

		if args.dont_change_comments:
			pass
		else:

			# Edit comment
			print "+Editing comment"
			if version_token in comment.body.encode("utf-8"):
				print ":Comment already constains '" + version_token + "', not editing"
			else:
				result = comment.edit(message)
				if result == None:
					print ":FAILED to edit comment"
				else:
					print ":Edited comment"
					edited_comments += 1
					
		# Delete the comment
		if args.delete_comments:
			print "+Deleting comment"
			result = comment.delete()
			if result == None:
				print ":FAILED to delete comment"
			else:
				print ":Deleted comment"
				deleted_comments += 1

		print "Processing complete for " + comment.permalink
		print

	# dump the comment results
	print "Comment Results:"
	print "Edited " + str(edited_comments) + " comments"
	print "Deleted " + str(deleted_comments) + " comments"
	print


except (NameError, TypeError) as e:
	pprint.pprint(dir(e))
	pprint.pprint(vars(e))
	raise SystemExit

except socket.timeout as e:
	pprint.pprint(dir(e))
	pprint.pprint(vars(e))
	print "FATAL: Timeout talking to Reddit.com"
	raise SystemExit

except urllib2.HTTPError as e:
	if e.code == 403:
		print ":FAILED the thing is too old and is read-only"
	else:
		print e.__module__,'.',e.__class__.__name__,':',e
		pprint.pprint(dir(e))
		pprint.pprint(vars(e))

except praw.errors.RateLimitExceeded as e:
	print "FATAL - You've exceeded the Reddit.com rate-limit. Don't run multiple instances of this script."
	raise SystemExit

except praw.errors.InvalidUserPass as e:
	print "FATAL - Reddit has rejected the username/password"
	raise SystemExit

except praw.errors.BadCaptcha as e:
	print "FATAL - Reddit.com is making user '" + args.username + "' solve captcha's, and we don't know how to do that."
	raise SystemExit

except praw.errors.ClientException as e:
	print "FATAL - Seems we've shit the bed."
	pprint.pprint(dir(e))
	pprint.pprint(vars(e))
	raise SystemExit

except praw.errors.APIException as e:
	if 'TOO_OLD' in e.error_type:
			# can't edit old things, reddit won't let us
			print ":FAILED the thing is too old and is read-only, sorry"
	else:
		pprint.pprint(dir(e))
		pprint.pprint(vars(e))
		raise SystemExit

except Exception as e:
	print e.__module__,'.',e.__class__.__name__,':',e
	pprint.pprint(dir(e))
	pprint.pprint(vars(e))
	print "Main loop failed with an exception, delaying 5 minutes before retrying"
	time.sleep(300)



print "Processing complete for " + username

print "Please visit /r/GoodbyeWorldBot if you have questions."

