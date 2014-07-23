for i in `seq 1 100`; do 
	completed=`mysql -utomb -pTolley0! hyperxTwitter -e "select COUNT(*) FROm handle where followers_updated is not null;" | tail -n1`;
	followers=`mysql -utomb -pTolley0! hyperxTwitter -e "select count(*) FROM follower;" | tail -n1`;
	echo "$completed complete";
	echo "$followers inserted";
	sleep 1m
done;
