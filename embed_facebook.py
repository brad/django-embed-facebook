'''
Created on Mar 10, 2011

@author: brad
'''

from django import template
from django.utils.html import strip_tags

from datetime import datetime
import json
import re
import urllib2

register = template.Library()

EMBED_FACEBOOK_MEDIA_URL = 'http://url/to/django_embed_facebook/static/'

@register.tag
def embed_facebook(parser, token):
    try:
        tag_name, fb_url = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, '%r tag requires a single argument' % token.contents.split()[0]
    
    if not (fb_url[0] == fb_url[-1] and fb_url[0] in ('"', "'")):
        raise template.TemplateSyntaxError, '%r tag\'s argument should be in quotes' % tag_name
    
    if not re.search('(http|https):\/\/www\.facebook\.com\/(.+)', fb_url):
        raise template.TemplateSyntaxError, '%r tag\'s argument must be a valid facebook url' % tag_name
    
    return EmbedFacebookNode(fb_url[1:-1])

class EmbedFacebookNode(template.Node):
    def __init__(self, fb_url):
        self.fb_url = fb_url
        
    def render_libs(self):
        return '<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>'+\
                '<script type="text/javascript" src="'+EMBED_FACEBOOK_MEDIA_URL+'slimbox2/js/slimbox2.js"></script>'+\
                '<link rel="stylesheet" href="'+EMBED_FACEBOOK_MEDIA_URL+'slimbox2/css/slimbox2.css" type="text/css" media="screen" />'+\
                '<link rel="stylesheet" href="'+EMBED_FACEBOOK_MEDIA_URL+'embed_facebook.css" type="text/css" media="screen" />'+\
                '<script type="text/javascript" src="'+EMBED_FACEBOOK_MEDIA_URL+'embed_facebook.js"></script>'
    
    def render_profile(self):
        result = ''
        if self.fb_url.find('pages/') != -1:
            fb_profile_url = 'http://graph.facebook.com/' + self.fb_url.split('/')[-1]
        else:
            fb_profile_url = 'http://graph.facebook.com/' + self.fb_url.split('www.facebook.com/')[1]
        response = urllib2.urlopen(fb_profile_url)
        fb_profile = json.loads(response.read())
    
        if not fb_profile.has_key('name'):
            result += '<a href="'+self.fb_url+'">'+self.fb_url+'</a></p>'
        else:
            result += '<div class="sohailfbbox">\n'
            if fb_profile['category'] == 'Television':
                result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+fb_profile['id']+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'images/page.png" style="vertical-align:text-top" /> '+fb_profile['name']+'<br /><span>'+fb_profile['category']+' ('+fb_profile['genre']+') &nbsp;|&nbsp; '+fb_profile['fan_count']+' fans &nbsp;|&nbsp; <a href="http://www.facebook.com/profile.php?id='+fb_profile['id']+'" target="_blank">View on Facebook</a></span></div>\n'
                result += '<div class="sohailfbboxbody">\n'
                result += '<p>'
                
                if fb_profile['network']:
                    result += 'Network: '+fb_profile['network']+' / ';
                if fb_profile['directed_by']:
                    result += 'Directed by: '+fb_profile['directed_by']+' / '
                if fb_profile['starring']:
                    result += 'Starring: '+fb_profile['starring']+''
                result += '</p>'            
                result += fb_profile['plot_outline']
                
            elif fb_profile['category'] == 'Public_figures_other':
                result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+fb_profile['id']+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'/images/page.png" style="vertical-align:text-top" /> '+fb_profile['name']+'<br /><span>Public Figure &nbsp;|&nbsp; '+fb_profile['fan_count']+' fans &nbsp;|&nbsp; <a href="http://www.facebook.com/profile.php?id='+fb_profile['id']+'" target="_blank">View on Facebook</a></span></div>\n'
                result += '<div class="sohailfbboxbody">\n'
                result += fb_profile['personal_info']
                
            else:
                result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+fb_profile['id']+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'/images/page.png" style="vertical-align:text-top" /> '+fb_profile['name']+'<br /><span>'+fb_profile['category']+((' '+fb_profile['genre']) if fb_profile.has_key('genre') else '')+' &nbsp;|&nbsp; '+((fb_profile['fan_count']+' fans') if fb_profile.has_key('fan_count') else (repr(fb_profile['likes'])+' people like this'))+' &nbsp;|&nbsp; <a href="http://www.facebook.com/profile.php?id='+fb_profile['id']+'" target="_blank">View on Facebook</a></span></div>\n' 
                result += '<div class="sohailfbboxbody">\n'

                description = fb_profile['company_overview'] if fb_profile.has_key('company_overview') else fb_profile['description']
                if len(description) < 500:
                    result += description.replace('\n','<br/>')
                else:
                    result += description[0:500].replace('\n','<br/>')+'<span id="'.fb_profile['id']+'" style="display:none">'+description[500:].replace('\n','<br/>')+'</span><span id="sohailmorelink'.fb_profile['id']+'">... <a href="javascript:void(0)" onclick="javascript:sohail_expand_content(\''+fb_profile['id']+'\')">See full description</a></span>'
        
            result += '</div>\n'
            result += '</div>\n'
        return result
    
    def render_album(self, args):
        result = ''
        fb_albums_url = 'http://graph.facebook.com/'+args['id']+'/albums?limit=400'
        response = urllib2.urlopen(fb_albums_url)
        fb_albums = json.loads(response.read())
    
        if not fb_albums.has_key('data'):
            result += '<a href="'+self.fb_url+'">'+self.fb_url+'</a></p>'
        else:
            for album in fb_albums['data']:                
                if album['link'].find(args['aid']) != -1:
                    result += '<div class="sohailfbbox">\n'
                    result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+album['from']['id']+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'images/photos.png" style="vertical-align:text-top" /> '+album['name'][0:60]+'<br /><span>By <a href="http://www.facebook.com/profile.php?id='+album['from']['id']+'" target="_blank">'+album['from']['name']+'</a> &nbsp;|&nbsp; <a href="'+album['link']+'" target="_blank">View on Facebook</a></span></div>\n'
                    result += '<div class="sohailfbboxbody">\n'

                    fb_photos_url = 'http://graph.facebook.com/'+album['id']+'/photos?limit='+('400' if not args.has_key('limit') else args['limit'])
                    response = urllib2.urlopen(fb_photos_url)
                    fb_photos = json.loads(response.read())                    
                    
                    if not fb_photos.has_key('data'):
                        result += '<p><a href="http://www.facebook.com/'+self.fb_url+'">www.facebook.com/'+self.fb_url+'</a></p>'
                    else:
                        for photo in fb_photos['data']:
                            result += '<a rel="lightbox-fb" href="'+photo['source']+'" title="'+('' if not photo.has_key('name') else photo['name'])+'"><img src="'+photo['picture']+'" class="sohailfbthumb" /></a>'
                    result += '</div>\n'
                    result += '</div>\n'
        return result
    
    def render_video(self, args):
        result = ''
        fb_video_url = 'http://www.facebook.com/video/video.php?v='+args['v']
        html = urllib2.urlopen(fb_video_url).read()
        title = re.search('<h3 class="video_title datawrap">(.*?)<\/h3>', html)
        owner = re.search('<a class="video_owner_link" href="(.*?)">(.*?)<\/a>', html)
        if not title:
            result += '<p><a href="'+self.fb_url+'">'+self.fb_url+'</a></p>'
        else:
            result += '<div class="sohailfbbox">\n'
            result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+owner.groups(0)[0].split('/')[-1]+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'images/video.png" style="vertical-align:text-top" /> '+title.groups(0)[0][0:70]+'<br /><span>By <a class="video_owner_link" href="'+owner.groups(0)[0]+'">'+owner.groups(0)[0]+'</a> &nbsp;|&nbsp; <a href="'+fb_video_url+'" target="_blank">View on Facebook</a></span></div>\n'
            result += '<div class="sohailfbboxbody">\n'
    
            result += '<object width="100%" height="40%" ><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="movie" value="http://www.facebook.com/v/'+args['v']+'" /><embed src="http://www.facebook.com/v/'+args['v']+'" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="100%" height="40%"></embed></object>'
            result += '</div>\n'
            result += '</div>\n'
        return result
    
    def render_photo(self, args):
        result = ''
        fb_photo_url = 'http://graph.facebook.com/'+args['fbid']
        response = urllib2.urlopen(fb_photo_url)
        fb_photo = json.loads(response.read())
    
        if not fb_photo.has_key('source'):
            result += '<a href="'+self.fb_url+'">'+self.fb_url+'</a></p>'
        else:
            result += '<div class="sohailfbbox">\n'
            result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+fb_photo['from']['id']+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'images/photos.png" style="vertical-align:text-top" /> '+(fb_photo['name'][0:60] if fb_photo.has_key('name') else '')+'<br /><span>By <a href="http://www.facebook.com/profile.php?id='+fb_photo['from']['id']+'" target="_blank">'+fb_photo['from']['name']+'</a> &nbsp;|&nbsp; <a href="'+fb_photo['link']+'" target="_blank">View on Facebook</a></span></div>\n'
            result += '<div class="sohailfbboxbody">\n'
            result += '<a rel="lightbox-fb" href="'+fb_photo['source']+'" title="'+(fb_photo['name'] if fb_photo.has_key('name') else '')+'"><img src="'+fb_photo['source'].replace('_s.jpg', '_a.jpg')+'" style="max-width:100%" /></a>'
            result += '</div>\n'
            result += '</div>\n'
        return result
    
    def render_event(self, args):
        result = ''
        fb_event_url = 'http://graph.facebook.com/'+args['eid']
        response = urllib2.urlopen(fb_event_url)
        fb_event = json.loads(response.read())
    
        if not fb_event.has_key('name'):
            result += '<a href="'+self.fb_url+'">'+self.fb_url+'</a></p>'
        else:
            datetime_format = '%Y-%m-%dT%H:%M:%S'
            start_time = datetime.strptime(fb_event['start_time'], datetime_format)
            end_time = datetime.strptime(fb_event['end_time'], datetime_format)
            location = (fb_event['location']+'<br/>') if fb_event.has_key('location') else ''
            if fb_event.has_key('venue'):
                address = fb_event['venue']['street'] if fb_event['venue'].has_key('street') else ''
                address += fb_event['venue']['city'] if fb_event['venue'].has_key('city') else ''
                address += fb_event['venue']['state'] if fb_event['venue'].has_key('state') else ''
                address += fb_event['venue']['country'] if fb_event['venue'].has_key('country') else ''
            result += '<div class="sohailfbbox">\n'
            result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+fb_event['owner']['id']+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'images/event.png" style="vertical-align:text-top" /> '+fb_event['name'][0:60]+'<br /><span>By <a href="http://www.facebook.com/profile.php?id='+fb_event['owner']['id']+'" target="_blank">'+fb_event['owner']['name']+'</a> &nbsp;|&nbsp; <a href="http://www.facebook.com/event.php?eid='+fb_event['id']+'" target="_blank">View on Facebook</a></span></div>\n'
            result += '<div class="sohailfbboxbody">\n'
            result += '<div class="sohailfbboxinfo"><b>When:</b> ';

            # If start and end time are in the same day, display the date only once, along with a time range
            if (end_time-start_time).days == 0:
                result += start_time.strftime('%b %-d, %Y')+' ('+start_time.strftime('%-I:%M %p')+' - '+end_time.strftime('%-I:%M %p')+')'
            else:
                result += start_time.strftime('%b %-d, %Y %-I:%M %p')+' - ' +end_time.strftime('%b %-d, %Y %-I:%M %p') 
            
            if fb_event.has_key('venue'):
                result += '<br /><br /><b>Where:</b> '+location+address+'<br /><br />&raquo; <a target="_blank" href="http://maps.google.com/maps?q='+address+'">View map</a>'
            result += '</div>'
            
            # If description is longer than 500 characters, display first 500 characters with "show more" link
            if len(fb_event['description']) > 500:
                result += fb_event['description'].replace('\n','<br/>')
            else:
                result += fb_event['description'][0:500].replace('\n','<br/>')+'<span id="'+fb_event['id']+'" style="display:none">'+fb_event['description'][500:].replace('\n','<br/>')+'</span><span id="sohailmorelink'+fb_event['id']+'">... <a href="javascript:void(0)" onclick="javascript:sohail_expand_content(\''+fb_event['id']+'\')">See full description</a></span>'

            result += '</div>\n'
            result += '</div>\n'
        return result
        
    def render_group(self, args):
        result = ''
        fb_group_url = 'http://graph.facebook.com/'+args['gid']
        response = urllib2.urlopen(fb_group_url)
        fb_group = json.loads(response.read())
    
        if not fb_group.has_key('name'):
            result += '<a href="'+self.fb_url+'">'+self.fb_url+'</a></p>'
        else:
            result += '<div class="sohailfbbox">\n'
            result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+fb_group['owner']['id']+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'images/photos.png" style="vertical-align:text-top" /> '+fb_group['name'][0:60]+'<br /><span>By <a href="http://www.facebook.com/profile.php?id='+fb_group['owner']['id']+'" target="_blank">'+fb_group['owner']['name']+'</a> &nbsp;|&nbsp; <a href="http://www.facebook.com/group.php?gid='+fb_group['id']+'" target="_blank">View on Facebook</a></span></div>\n'
            result += '<div class="sohailfbboxbody">\n'
            
            # If description is longer than 500 characters, display first 500 characters with "show more" link
            if len(fb_group['description']) > 500:
                result += fb_group['description'].replace('\n','<br/>')
            else:
                result += fb_group['description'][0:500].replace('\n','<br/>')+'<span id="'+fb_group['id']+'" style="display:none">'+fb_group['description'][500:].replace('\n','<br/>')+'</span><span id="sohailmorelink'+fb_group['id']+'">... <a href="javascript:void(0)" onclick="javascript:sohail_expand_content(\''+fb_group['id']+'\')">See full description</a></span>'

            result += '</div>\n'
            result += '</div>\n'
        return result
        
    def render_note(self, args):
        result = ''
        fb_note_url = 'http://www.facebook.com/note.php?note_id='+args['note_id']
        html = urllib2.urlopen(fb_note_url).read()
        title = re.search('<h2 class="uiHeaderTitle">(.*?)<\/h2>', html)
        owner = re.search('<div class="mbs mbs uiHeaderSubTitle lfloat fsm fwn fcg">by <a href="(.*?)">(.*?)<\/a>', html)
        note = re.search('<div class="mbl notesBlogText clearfix"><div>(.*?)<\/div><\/div>', html)
    
        if not title:
            result += '<a href="'+self.fb_url+'">'+self.fb_url+'</a></p>'
        else:
            result += '<div class="sohailfbbox">\n'
            result += '<div class="sohailfbboxhead"><img src="http://graph.facebook.com/'+owner.groups(0)[0].split('/')[-1]+'/picture" align="left" style="margin-right:10px; width:40px; height:40px;" /><img src="'+EMBED_FACEBOOK_MEDIA_URL+'images/note.png" style="vertical-align:text-top" /> '+title.groups(0)[0][0:70]+'<br /><span>By <a href="'+owner.groups(0)[0]+'">'+owner.groups(0)[1]+'</a> &nbsp;|&nbsp; <a href="http://www.facebook.com/note.php?note_id='+args['note_id']+'" target="_blank">View on Facebook</a></span></div>\n'
            result += '<div class="sohailfbboxbody">\n'
            result += strip_tags(note.groups(0)[0])
            result += '</div>\n'
            result += '</div>\n'
        return result
    
    def render(self, context):
        content = self.render_libs() if not context.has_key('static_files_loaded') else ''
        context['static_files_loaded'] = True
        if self.fb_url.find('?') == -1:
            content += self.render_profile()
        else:
            query = self.fb_url.split('?')[1]
            args = {}
            for arg in query.split('&'):
                args[arg.split('=')[0]] = arg.split('=')[1]
            if re.search('(http|https):\/\/www\.facebook\.com\/album.php.+', self.fb_url):
                content += self.render_album(args)
            elif re.search('(http|https):\/\/www\.facebook\.com\/video\/video.php.+', self.fb_url):
                content += self.render_video(args) 
            elif re.search('(http|https):\/\/www\.facebook\.com\/photo.php.+', self.fb_url):
                content += self.render_photo(args) 
            elif re.search('(http|https):\/\/www\.facebook\.com\/event.php.+', self.fb_url):
                content += self.render_event(args) 
            elif re.search('(http|https):\/\/www\.facebook\.com\/group.php.+', self.fb_url):
                content += self.render_group(args) 
            elif re.search('(http|https):\/\/www\.facebook\.com\/note.php.+', self.fb_url):
                content += self.render_note(args)
            else:
                content = '<p><a href="'+self.fb_url.split('?')[0]+'" target="_blank">'+self.fb_url.split('?')[0]+'</a></p>'
        
        return content
