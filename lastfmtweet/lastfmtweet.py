#!/usr/local/bin/python2.7
# encoding: utf-8
'''
lastfmtweet -- shortdesc

lastfmtweet is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2014 organization_name. All rights reserved.

@license:    license

@contact:    user_email
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

__all__ = []
__version__ = 0.1
__date__ = '2014-11-15'
__updated__ = '2014-11-15'

DEBUG = 1
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
    
    hardcoded_blacklist=[
                         'comptines',
                         ]
    
    regex = re.compile('%s'%string.join(hardcoded_blacklist,'|'),re.I)
    return regex.search(name)
            
    

def get_print_list(username,top,period):
    
    url='http://ws.audioscrobbler.com/2.0/user/%s/top%ss.xml?period=%s' % (username,top,period)
    print url
    
    try:
        raw_xml = urllib2.urlopen(url)
    except Exception, e:
        raise CLIError(e)
        
    print_list=[]
    charts=ElementTree.fromstring(raw_xml.read())
    
    if top == 'artist':
        for artist in charts.findall('artist'):
            print_list.append(artist.find('name').text)
    elif top == 'album':
        for album in charts.findall('album'):
            for artist in album.findall('artist'):
                print_list.append("%s - %s" % (artist.find('name').text, album.find('name').text))
    elif top == 'track':
        for track in charts.findall('track'):
            for artist in track.findall('artist'):
                print_list.append("%s - %s" % (artist.find('name').text, track.find('name').text))
    else:
        raise CLIError(Exception("unknown type %s" % top))
        
    return print_list


def summarize(print_list, prefix='', limit=140):
    text=prefix
    for add in print_list:
        
        if not blacklist(add):
            new_len = len(text) + len(add) +1
            if new_len > limit:
                break
            else:
                text += "\n" + add
    return text

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

  Created by user_name on %s.
  Copyright 2014 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument("-u", "--username", dest="username", action="store",
                            required=True, help="LastFM username [default: %(default)s]")
        parser.add_argument("-i", "--tweet", dest="tweet", action="store", help="Tweet to this URL [default: %(default)s]")
        
        parser.add_argument("-p", "--period", dest="period", action="store",
                            default='3month',help="LastFM period [default: %(default)s]")
        parser.add_argument("-t", "--top", dest="top", choices=['album','artist','track'],
                            default ='artist', help="Chart type [default: %(default)s]")
                
        # Process arguments
        args = parser.parse_args()

        username = args.username
        period = args.period
        top = args.top
        verbose = args.verbose
        tweet = args.tweet
        

        if verbose > 0:
            print("Verbose mode on")
            if tweet:
                print("Tweet mode on")
            else:
                print("Tweet mode off")

        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
    
    month=date.today().strftime('%b')
    text = summarize(get_print_list(username,top,period), prefix="Top %ss %s:"% (top,month), limit=160)
    
    if tweet:
        pass
    else:
        print text
        
    if verbose > 0:
            print("Done")

if __name__ == "__main__":
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-unomorsad")
        sys.argv.append("-talbum")
        sys.argv.append("-p1month")
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