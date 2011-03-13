&copy; Brad Pitcher <brad@onewheelweb.com>, 2011

django-embed-facebook
=====================
This is a django port of the [embed-facebook](http://wordpress.org/extend/plugins/embed-facebook/) plugin for WordPress. I tested all different kind of links, but if I missed something please file a bug.

Dependencies
============
Slimbox2: Download [here](http://code.google.com/p/slimbox/) and copy the css and js folder into static/slimbox2

How to use
==========
Installation
------------
Download the files. Move files in the static folder somewhere that you can serve them. Move embed_facebook.py to the templatetags folder of your django app and change the EMBED_FACEBOOK_MEDIA_URL variable to point to the location of the static files you just placed.

Usage
-----
In a template where you wish to embed facebook items add this line:
{% load embed_facebook %}

Now just use the template tag like so:
{% embed_facebook "http://www.facebook.com/video/video.php?v=753935859715" %}

And it will find your content on facebook and display it nicely on your page. It works like in the demos [here](http://wp.sohailabid.com/)
