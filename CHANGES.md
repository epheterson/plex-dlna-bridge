# Changes from the original

This is a modified version of [songchenwen/plexdlnaplayer](https://github.com/songchenwen/plexdlnaplayer), as required by the GPL. Everything below has also been offered upstream in [songchenwen/plexdlnaplayer#25](https://github.com/songchenwen/plexdlnaplayer/pull/25).

## 2026-08-10

**Support renderers advertising v2 UPnP services.**
Some renderers advertise `AVTransport:2` and `RenderingControl:2` instead of the v1 services the original looks up by constant. Two separate problems: service lookup rejected such a device outright, and `xml2dict`'s namespace map listed only the v1 URIs, so every SOAP reply key stayed fully qualified and `info.Envelope.Body.get(f"{action}Response")` returned `None` for every call with a response. Commands still worked, so playback started, but position, volume, mute and transport state came back empty. Service lookup now accepts another version of the same service (highest wins), the namespace map covers versions 1–4, and a missing response key is reported rather than silently returned as `None`.

**Handle an empty or whitespace `modelDescription`.**
An empty `<modelDescription/>` parses to `None`, and a `.get(key, default)` default never applies because the key exists — so `None` reached an outgoing HTTP header and 500'd the pairing page. Some devices send a single space instead, which is truthy and therefore survives an `or` fallback. Both are handled by stripping. Upstream [#22](https://github.com/songchenwen/plexdlnaplayer/issues/22); the whitespace case was found by @tschechniker in upstream [#14](https://github.com/songchenwen/plexdlnaplayer/pull/14).

**Fix `response.status_code` on aiohttp responses.**
`control()` built its error message with `response.status_code`, which aiohttp responses do not have, so any non-2xx reply from a device raised `AttributeError` and hid the real status. Upstream [#18](https://github.com/songchenwen/plexdlnaplayer/issues/18).

**`FORCE_HTTP` and `PLEX_LAN_ADDRESS` (opt-in, default off).**
Some renderers cannot fetch HTTPS. At least one does not merely fail on Plex's `plex.direct` TLS URL — it drops its own UPnP control server, which then presents as a device that went offline. `FORCE_HTTP` rewrites the address to a plain `http://` LAN one. `PLEX_LAN_ADDRESS` supplies that address explicitly, which is required when the controller reaches Plex over IPv6, since nothing usable can be derived from the IPv6 form of a plex.direct hostname.

**Diagnostics.**
`on_new_dlna_device` now logs why a device was skipped, so an unsupported renderer is distinguishable from one that was never discovered. The state loop's error print sat behind `if __debug__` while the image ran `python -OO`, which compiles those out; that one print is now unconditional; `-OO` is retained so per-poll debug output stays suppressed. `PYTHONUNBUFFERED` is set so `print()` output actually reaches `docker logs`.

**Build.**
Pinned the base image to `python:3.10`. With an unpinned `python:3` the pinned cchardet/httptools/uvloop wheels no longer build, so the image no longer built from source.

**Tests.**
Added unit tests for the service-version helpers.
