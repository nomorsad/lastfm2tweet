#!/usr/bin/env python2
# encoding: utf-8
'''
lastfmtweet -- Publish Lastfm charts on Twitter

@author:     nomorsad

@copyright:  2014 organization_name. All rights reserved.

@license:    GPLv3 or

@contact:    nomorsad.poubelle@gmail.com
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

import urllib2
from defusedxml import ElementTree
import re
import string
from datetime import date
import tweepy
import json

__all__ = []
__version__ = 0.1
__date__ = '2014-11-15'
__updated__ = '2014-11-15'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def blacklist(name):
    '''hardcoded list of excluded items'''
    
    #TODO: move list into config file
    hardcoded_blacklist=[
                         'comptines',
                         ]
    
    regex = re.compile('%s'%string.join(hardcoded_blacklist,'|'),re.I)
    return regex.search(name)
            
    

def get_print_list(username,chart,period):
    '''return LastFM XML chart as a simple list'''
    
    url='http://ws.audioscrobbler.com/2.0/user/%s/top%ss.xml?period=%s' % (username,chart,period)
    print url
    raw_xml = urllib2.urlopen(url)

    print_list=[]
    charts=ElementTree.fromstring(raw_xml.read())
    
    if chart == 'artist':
        for artist in charts.findall('artist'):
            print_list.append(artist.find('name').text)
    elif chart == 'album':
        for album in charts.findall('album'):
            for artist in album.findall('artist'):
                print_list.append("%s - %s" % (artist.find('name').text, album.find('name').text))
    elif chart == 'track':
        for track in charts.findall('track'):
            for artist in track.findall('artist'):
                print_list.append("%s - %s" % (artist.find('name').text, track.find('name').text))
    else:
        raise CLIError(Exception("unknown type %s" % chart))
        
    return print_list


def summarize(print_list, prefix='', limit=140):
    '''prepare message to be published'''
    text=prefix
    for add in print_list:
        
        if not blacklist(add):
            new_len = len(text) + len(add) +2
            if new_len > limit:
                break
            else:
                text += "\n " + add
    return text


def publish_twitter(text):
    '''publish a status on Twitter'''
    
    config_file=os.path.join(os.environ['HOME'],'.lastfm2tweet')
    try:
        config = open(config_file)
    except IOError, e:
        raise Exception('%s' % e)
            
    json_data = config.read()
    
    oauth_param = json.loads(json_data)
    
    for param in ('consumer_key','consumer_secret','key','secret'):
        if param not in oauth_param:
            raise Exception('missing param %s in config file' % param)
        
        #workaround of fucking HMAC function
        oauth_param[param] = oauth_param[param].encode('ascii')
    
    auth = tweepy.OAuthHandler(oauth_param['consumer_key'], oauth_param['consumer_secret'])
    auth.set_access_token(oauth_param['key'], oauth_param['secret'])
    print "Authenticated as %s" % auth.get_username()
    api = tweepy.API(auth)
    api.update_status(text)



def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by nomorsad on %s.
  Copyright 2014 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, program_version_message)

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument("-u", "--username", dest="username", action="store",
                            required=True, help="LastFM username [default: %(default)s]")
        parser.add_argument("-p", "--period", dest="period", action="store",
                            default='3month',help="LastFM period [default: %(default)s]")
        parser.add_argument("-c", "--chart", dest="chart", choices=['album','artist','track'],
                            default ='artist', help="Chart type [default: %(default)s]")
        
        parser.add_argument("-t", "--tweet", dest="tweet", action="store_true", help="Publish to Twitter [default: %(default)s]")
                
        # Process arguments
        args = parser.parse_args()

        username = args.username
        period = args.period
        chart = args.chart
        verbose = args.verbose
        tweet = args.tweet
        

        if verbose > 0:
            print("Verbose mode on")
            if tweet:
                print("Tweet mode on")
            else:
                print("Tweet mode off")

        month=date.today().strftime('%b')
        text = summarize(get_print_list(username,chart,period), prefix="Top %ss for %s from last.fm:\n"% (chart,month))
        
        if tweet:
            publish_twitter(text)
        else:
            print text
            
        if verbose > 0:
                print("Done")


    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2
    
    
    
    
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'lastfmtweet_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
