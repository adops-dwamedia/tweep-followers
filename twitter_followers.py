import tweepy
import time
import sys
import MySQLdb as mdb
import json

from warnings import filterwarnings
filterwarnings('ignore', category = mdb.Warning)



def get_subscribers(screen_name):
	ids = []
	for page in tweepy.Cursor(api.followers_ids, screen_name = screen_name).pages():
		ids.extend(page)
		time.sleep(60)
	return ids


def db_connect(user,pw,db="",host="localhost"):

# get db handle: 
        try:
                if db == "":
                        con = mdb.connect(host, user, pw)
                else:
                        con = mdb.connect(host, user, pw, db)
                cur = con.cursor()
                return con,cur
        except mdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
                sys.exit(1)


def build_db(cur,handle_data, drop=False):
	if drop:
		cur.execute("drop database if exists hyperxTwitter")
	cur.execute("create database if not exists hyperxTwitter")
	cur.execute("use hyperxTwitter")
	stmt = "create table if not exists handle" + \
			"(" + \
			"handle VARCHAR(255)," + \
			"twitterid INT," + \
			"url VARCHAR(255)," + \
			"team_individual VARCHAR(255)," + \
			"team VARCHAR(255)," + \
			"game VARCHAR(255)," + \
			"hyperx_logo TINYINT," + \
			"hyperx_logo_featured TINYINT," + \
			"tweets_count INT," + \
			"PRIMARY KEY (handle)" + \
			");"
	cur.execute(stmt)

	stmt = "create table if not exists follower " + \
			"(" + \
			"followerID INT," + \
			"followedID INT," + \
			"date_observed DATETIME," +\
			"PRIMARY KEY (followerID, followedID)" +\
			");"
	cur.execute(stmt)		

	stmt = 	"load data local infile '%s'"%handle_data +\
			"into table handle " + \
			"fields terminated by ','" + \
			"lines terminated by '\\n'" + \
			"ignore 1 lines" 
	cur.execute(stmt)
def pause_wrapper(default_limit=180, remaining=180, default_reset_window = 15*60 + 2, reset_time= time.time() + 15*60 + 2):
	def decorator(f):
		config = [remaining,reset_time]
		def inner(*args,**kwargs):
			config[0] = config [0]-1
			if config[0] <= 0:
				print "limit reached for %s, waiting %s seconds."%(f.__name__, round(config[1]-time.time()))
				time.sleep(config[1] - time.time())
				config[0] = default_limit
				config[1] = time.time() + default_reset_window
			return f(*args,**kwargs)
		return inner
	return decorator
			
def update(cur, api, wait = 60):
	""" updates db to fill in null values for twitterid or tweets_count """
	cur.execute("select handle from handle where twitterid is null or tweets_count is null")
	handles = (r[0] for r in cur.fetchall())
	
	for h in handles:
		user = api.get_user(h)
		uID = user.id
		tweets_count = user.statuses_count
		cur.execute("update handle set twitterid = %s, tweets_count = %s where handle = '%s'"%(uID, tweets_count, h))

def get_api_status():
	""" prints all api method statuses that are not at full quota"""
	lstatus = api.rate_limit_status()['resources']
        for r in lstatus:
                for m in lstatus[r]:
                        if lstatus[r][m]['limit'] != lstatus[r][m]['remaining']:
                                print r, m, lstatus[r][m]
		
	



if __name__ == "__main__":
	with open('twitter.json') as f:
		auths = json.loads(f.read())

	consumer_key = auths["consumer_key"]
	consumer_secret = auths["consumer_secret"]
	access_token = auths["access_token"]
	access_token_secret = auths["access_token_secret"]

	auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth)


	# remake api functions to respect rate limits.  
	lstatus = api.rate_limit_status()['resources']

	remaining, reset_time = lstatus["users"]["/users/show/:id"]["remaining"], lstatus["users"]["/users/show/:id"]["reset"]

	
	api.get_user = pause_wrapper(remaining = remaining, reset_time = reset_time)(api.get_user)
	api.followers_ids = pause_wrapper()(api.followers_ids)


	con,cur = db_connect("tomb", "Tolley0!",host="184.105.184.30")
	build_db(cur, "twitter_handles.csv", True)
	update(cur,api,1)
	
	get_api_status()
	
	if con:
		con.commit()
		con.close()	
