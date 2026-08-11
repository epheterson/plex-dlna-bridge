"""Plex DLNA Bridge.

A modified version of songchenwen/plexdlnaplayer (https://github.com/songchenwen/plexdlnaplayer),
carrying fixes for renderers advertising v2 UPnP services, devices that cannot fetch HTTPS,
and the container build. See CHANGES.md for the full list.

Licensed under the GPL-3.0, as the original is.
"""

from plex.plexserver import start_plex_server

if __name__ == "__main__":
    start_plex_server()
