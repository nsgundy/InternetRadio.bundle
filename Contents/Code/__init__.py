ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

PLAYLIST_URL_AAC = 'http://www.radioparadise.com/musiclinks/rp_128aac.m3u'
PLAYLIST_URL_MP3 = 'http://www.radioparadise.com/musiclinks/rp_128.m3u'
METADATA_URL = 'http://radioparadise.com/ajax_xml_song_info.php?song_id=now'

PREFIX = '/music/InternetRadio'

####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
    # Initialize the plugin
    Plugin.AddViewGroup('List', viewMode = 'List', mediaType = 'items')
    Plugin.AddViewGroup('InfoList', viewMode = 'InfoList', mediaType = 'items')

    # Setup the artwork associated with the plugin
    ObjectContainer.title1 = 'Internet Radio'
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = 'List'

    DirectoryObject.thumb = R(ICON)

    TrackObject.thumb = R(ICON)
    TrackObject.art = R(ART)

####################################################################################################

@handler(PREFIX, 'Internet Radio')
def MainMenu():
    oc = ObjectContainer(no_cache = True)

    # Would love to call this periodically to update the channel background art, but not possible
    # oc.art = HTTP.Request('http://radioparadise.com/readtxt.php').content

    # Fetch XML with metadata and build XML Object
    song_info = XML.ObjectFromURL(METADATA_URL)

    # Fetch AAC and MP3 urls
    aac_url = HTTP.Request(PLAYLIST_URL_AAC).content.splitlines()[0]
    mp3_url = HTTP.Request(PLAYLIST_URL_MP3).content.splitlines()[0]
    
    # Add playable TrackObject to menu structure
    oc.add(
        CreateTrackObject(
            title = song_info.title.text,
            artist = song_info.artist.text,
            album = song_info.album.text,
            rating = float(song_info.rating.text),
            thumb = song_info.large_cover.text,
            art = song_info.image.large_url.text,
            aac_url = aac_url,
            mp3_url = mp3_url
        )
    )

    return oc

####################################################################################################
@route(PREFIX + '/CreateTrackObject', rating = float, include_container = bool) 
def CreateTrackObject(title, artist, album, rating, thumb, art, aac_url, mp3_url, include_container=False):        
    track_object = TrackObject(
        key = 
            Callback(
                CreateTrackObject,
                title = title,
                artist = artist,
                album = album,
                rating = rating,
                thumb = thumb,
                art = art,
                aac_url = aac_url,
                mp3_url = mp3_url,
                include_container = True
            ),
        rating_key = title,
        title = title,
        artist = artist,
        album = album,
        rating = rating,
        thumb = thumb,
        art = art
    )
    
    track_object.add(
        MediaObject(
            container = Container.MP3,
            audio_codec = AudioCodec.MP3,
            audio_channels = 2,
            bitrate = 128,
            parts = [
                PartObject(
                    key = Callback(PlayMP3, url = mp3_url)
                )
            ]
        )
    )
    
    track_object.add(
        MediaObject(
            container = Container.MP4,
            audio_codec = AudioCodec.AAC,
            audio_channels = 2,
            bitrate = 128,
            parts = [
                PartObject(
                    key = Callback(PlayAAC, url = aac_url)
                )
            ]
        )
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object
        
#################################################################################################### 
@route(PREFIX + '/PlayMP3.mp3')
def PlayMP3(url):
    return PlayAudio(url)
    
#################################################################################################### 
@route(PREFIX + '/PlayAAC.aac')
def PlayAAC(url):
    return PlayAudio(url)
    
#################################################################################################### 
def PlayAudio(url):
    return Redirect(url)
