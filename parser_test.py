from optparse import OptionParser

parser = OptionParser()
parser.set_defaults(tweet=False)
parser.set_defaults(update=False)
parser.add_option("-t", "--tweet", dest="tweet",
                  action="store_true",
                  help = "to kick tweet_msg().")
parser.add_option("-u", "--update", dest="update",
                  action="store_true",
                  help = "to kick update_info().")

(options, args) = parser.parse_args()

print options
print args