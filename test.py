import time


def wait(secs):
        if secs <= 60:
                print "waiting %s seconds"%secs
        else:   
                mins = secs / 60
                remaind = secs%60
                print "waiting %s minutes"%(round(secs/60.0,2))
                time.sleep(remaind)
                for i in reversed(range(mins)):
                        print "\t%s min remaining"%(i + 1)
                        time.sleep(60)






wait(86)
