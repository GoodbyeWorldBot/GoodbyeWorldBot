#!/bin/python

import time
import praw
import socket
import pprint
import urllib2
import optparse

version = "1.1"
version_token = "GoodbyeWorldBot_v" + version

# ver	dd/mm/yyyy	/u/whoever-did-change	detail
# v1.0	14/10/2012	/u/GoodbyeWorldBot	Initial version
# v1.1	15/10/2012	/u/GoodbyeWorldBot	Added better output, optional delete comments


user_agent = "/u/GoodbyeWorldBot v" + version + " by /r/GoodbyeWorld"

message = "The owner of this account has requested this content be removed by /u/GoodbyeWorldBot\n\nVisit /r/GoodbyeWorld for more information.\n\n" + version_token


delete_comments = False
verbose = False

parser = OptionParser()
parser.add_option("-v", "--verbose",			action="store_true", dest="verbose", 			default=False, help="Detailed output during processing")
parser.add_option("-e", "--edit_comments", 		action="store_true", dest="edit_comments", 		default=True, help="Edit comments and self-post text to contain the GoodbyeWorldBot deletion notice")
parser.add_option("-E", "--edit_submissions", 	action="store_true", dest="edit_submissions", 	default=False, help="Delete comments")
parser.add_option("-d", "--delete_comments", 	action="store_true", dest="delete_comments", 	default=False, help="Delete comments")
parser.add_option("-D", "--delete_submissions", action="store_true", dest="delete_submissions", default=True,  help="")
parser.add_option("-p", "--s)
parser.add_option("-U", "--user", username)
parser.add_option("-P", "--passwd", password)



print "Using the following message when editing self-posts and comments:"
print "~~~~~~~~~~~~~~~~~~~~~~~~~"
print message
print "~~~~~~~~~~~~~~~~~~~~~~~~~"
print

r = praw.Reddit(user_agent=user_agent)
r.login(username=username, password=password)

user = r.get_redditor(username)

submissions = None
deleted_submissions = 0
commented_submissions = 0
edited_submissions = 0

submissions = user.get_submitted(limit=None)
pprint.pprint(dir(submissions))
for submission in submissions:
	print "========================="
	print "Processing submission " + submission.short_link
	print submission.title.encode("utf-8")
	print "-------------------------"

	# Edit self-post text
	print "+Checking if this is a self-post"
	if submission.is_self:
		print ":detected this is a self-post"
		print ":body:"
		print "~~~~~~~~~~~~~~~~~~~~~~~~~"
		print submission.selftext.encode("utf-8")
		print "~~~~~~~~~~~~~~~~~~~~~~~~~"
				
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
	else:
			print ":It's not a self-post"
			
	# Add a comment to the submission
	print "+Adding comment"
	result = None
	try:
		result = submission.add_comment(message)

	except (NameError, TypeError) as e:
		print e.__class__.__name__,':',e
		pprint.pprint(dir(e))
				pprint.pprint(vars(e))
				break
		except socket.timeout as e:
				print e.__module__,'.',e.__class__.__name__,':',e
				pprint.pprint(dir(e))
				pprint.pprint(vars(e))
				print "Timeout"
	except urllib2.HTTPError as e:
		if e.code == 403:
			print ":FAILED the thing is too old and is read-only"
		else:
					print e.__module__,'.',e.__class__.__name__,':',e
					pprint.pprint(dir(e))
					pprint.pprint(vars(e))
		except Exception as e:
				if hasattr(e, 'error_type'):
			if 'TOO_OLD' in e.error_type:
							print ":FAILED the thing is too old and is read-only"
				else:
						#print e.__module__,'.',e.__class__.__name__,':',e
						pprint.pprint(dir(e))
						pprint.pprint(vars(e))
						print "Main loop failed with an exception, delaying 5 minutes before retrying"
						time.sleep(300)

	if result == None:
		print ":FAILED to add comment to submission"
	else:
		print ":Added comment to submission"
		commented_submissions += 1
				
	# Delete the submission
	print "+Attempting to delete submission"
	result = submission.delete()
	if result == None:
		print ":FAILED to delete submission"
	else:
		print ":Deleted submission"
		deleted_submissions += 1

	print "Processing complete for " + submission.short_link
	print


print 
print "Results:"
print "Commented on " + str(commented_submissions) + " submissions"
print "Edited self-post text on " + str(edited_submissions) + " submissions"
print "Deleted " + str(commented_submissions) + " submissions"
print
print "Taking a break so you can CTRL-C if needed"
time.sleep(5)
print "Moving on then.."



# On to the comments!
comments = None
edited_comments = 0
deleted_comments = 0

comments = user.get_comments(limit=None)
for comment in comments:
	print "========================="
	print comment.permalink
	print "-------------------------"

	print "Comment body:"
	print "~~~~~~~~~~~~~~~~~~~~~~~~~"
	print comment.body.encode("utf-8")
	print "~~~~~~~~~~~~~~~~~~~~~~~~~"

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
	if delete_comments:
		print "+Deleting comment"
		result = comment.delete()
		if result == None:
			print ":FAILED to delete comment"
		else:
			print ":Deleted comment"
			deleted_comments += 1
	else:
		print "+Not deleting comment, leaving as edited"

	print "Processing complete for " + comment.permalink
	print


print
print "Results:"
print "Edited " + str(edited_comments) + " comments"
print "Deleted " + str(deleted_comments) + " comments"
print


print "Processing complete for " + username

