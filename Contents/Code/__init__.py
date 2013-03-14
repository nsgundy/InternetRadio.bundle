ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

PLAYLIST_URL_AAC = 'http://www.radioparadise.com/musiclinks/rp_128aac.m3u'
PLAYLIST_URL_MP3 = 'http://www.radioparadise.com/musiclinks/rp_128.m3u'
METADATA_URL = 'http://radioparadise.com/ajax_xml_song_info.php?song_id=now'

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

@handler('/music/InternetRadio', 'Internet Radio')
def MainMenu():
    oc = ObjectContainer(view_group='InfoList')

    # Would love to call this periodically to update the channel background art, but not possible
    # oc.art = HTTP.Request('http://radioparadise.com/readtxt.php').content

    # Fetch XML with metadata and build XML Object
    song_info = XML.ObjectFromURL(METADATA_URL)

    # Extract interesting elements from metadata XML Object and build a metadate dictionary
    metadata_dict = dict(
        title = song_info.title.text,
        artist = song_info.artist.text,
        album = song_info.album.text,
        rating = float(song_info.rating.text),
        thumb = song_info.large_cover.text,
        art = song_info.image.large_url.text
    )

    # Fetch AAC playlist and create a list from it
    playlist = [track for track in HTTP.Request(PLAYLIST_URL_AAC).content.splitlines()]
    
    # Add playable TrackObject to menu structure - using AAC playlist
    oc.add(CreateTrackObject(
        metadata_dict = metadata_dict,
        # Add all tracks in playlist, currently doesn't work, adding single track instead
        #playlist = playlist,
        playlist = [playlist[0]],
        container = Container.MP4,
        audio_codec = AudioCodec.AAC,
        audio_channels = 2,
        bitrate = 128000
    ))

    # Fetch MP3 playlist and create a list from it
    playlist = [track for track in HTTP.Request(PLAYLIST_URL_MP3).content.splitlines()]
    
    # Add playable TrackObject to menu structure - using MP3 playlist
    oc.add(CreateTrackObject(
        metadata_dict = metadata_dict,
        # Add all tracks in playlist, currently doesn't work, adding single track instead
        #playlist = playlist,
        playlist = [playlist[0]],
        container = Container.MP3,
        audio_codec = AudioCodec.MP3,
        audio_channels = 2,
        bitrate = 128000
    ))

    return oc

# Build a track object with potentially multiple PartObjects (currently not working)
def CreateTrackObject(metadata_dict, playlist, container, audio_codec, audio_channels, bitrate):
    track_object = TrackObject(
        key = ObjectContainer(objects=[TrackObject()]),
        rating_key = playlist[0],
        title = metadata_dict['title'],
        artist = metadata_dict['artist'],
        album = metadata_dict['album'],
        rating = metadata_dict['rating'],
        thumb = metadata_dict['thumb'],
        art = metadata_dict['art'],
        items = [MediaObject(
            parts = [PartObject(key=track) for track in playlist],
            container = container,
            audio_codec = audio_codec,
            audio_channels = audio_channels,
            bitrate = bitrate
        )]
    )
    return track_object

# Not currently used, don't like how we are duplicating effort for the "key"
#def CreateTrackObject(url, title, container, audio_codec, include_container=False):
#    track_object = TrackObject(
#        key = Callback(CreateTrackObject, url=url, title=title, container=container, audio_codec=audio_codec, include_container=True),
#        rating_key = url,
#        title = title,
#        items = [
#            MediaObject(
#                parts = [
#                    PartObject(key=url)
#                ],
#                container = container,
#                audio_codec = audio_codec,
#                audio_channels = 2
#            )
#        ]
#    )
#
#    if include_container:
#        return ObjectContainer(objects=[track_object])
#    else:
#        return track_object