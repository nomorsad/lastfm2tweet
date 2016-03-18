lastfm2tweet
============

CLI to push Last.fm charts as tweets

Configuration
-------------

Create file .lastfm2tweet in your home directory as json format:

```
{
    "lastfm_apikey": "",
    "consumer_key": "",
    "consumer_secret": "",
    "key": "",
    "secret": ""
}
```

You can obtain `lastfm_apikey` on http://www.last.fm/api.

To get the other needed OAuth stuff, go to https://apps.twitter.com/ and create your own application to get `consumer_key` and `consumer_secret`.
Then click on *Generate Token Access* to get your personnal `key` and `secret`.
