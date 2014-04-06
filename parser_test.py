from optparse import OptionParser

def handle_options():
    parser = OptionParser()
    parser.set_defaults(tweet=False)
    parser.set_defaults(update=False)
    parser.add_option("-t", "--tweet", dest="tweet",
                      action="store_true",
                      help = "to kick tweet_msg().")
    parser.add_option("-u", "--update", dest="update",
                      action="store_true",
                      help = "to kick update_info().")
    return parser.parse_args()

if __name__=="__main__":

    (options, args) = handle_options()
 
    print options
    print options.tweet
    print options.update
    print args