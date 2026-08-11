# Plex DLNA Bridge

Cast Plex and Plexamp to any UPnP/DLNA renderer — an amplifier, a network streamer, a pair of active speakers — in **bit-perfect quality**.

Your renderer appears in Plex's `Select Player` window and in Plexamp's output list. The renderer then fetches the original file straight from your Plex server, so a 24-bit FLAC arrives untouched. That is the point of this project: AirPlay and Chromecast both cap or re-encode the stream, and if CD quality were enough you would not need any of this.

> **Credit where it is due.** This is based on [songchenwen/plexdlnaplayer](https://github.com/songchenwen/plexdlnaplayer), which did all of the hard work: UPnP discovery, Plex GDM announcements, the play-queue and timeline handling that make a dumb renderer look like a Plex player. That project has not seen a commit since 2021 and its issue tracker has gone unanswered, so this exists to keep it alive and working.
>
> Everything here has been offered back upstream in [songchenwen/plexdlnaplayer#25](https://github.com/songchenwen/plexdlnaplayer/pull/25). **If that is ever merged, this repository becomes redundant** — and that is a good outcome, not a rivalry.

## What this fixes

The upstream project stopped working, or worked only partially, on a lot of hardware. All of the following are fixed here:

- **Renderers advertising v2 UPnP services** (`AVTransport:2` / `RenderingControl:2`) were rejected outright. Worse, when forced through, every SOAP reply parsed as `None` — so playback started but position, volume and transport state stayed permanently empty, with nothing logged. Affects many modern amplifiers, including Hegel and other Rygel-based stacks.
- **Devices sending an empty or whitespace `<modelDescription/>`** crashed the pairing page with a 500 (`TypeError: Cannot serialize non-str key None`). Reported upstream as [#22](https://github.com/songchenwen/plexdlnaplayer/issues/22) and [#14](https://github.com/songchenwen/plexdlnaplayer/pull/14).
- **`AttributeError: 'ClientResponse' object has no attribute 'status_code'`** masked the real error whenever a device replied with a non-2xx status. Reported upstream as [#18](https://github.com/songchenwen/plexdlnaplayer/issues/18).
- **Renderers that cannot fetch HTTPS.** Plex hands out an `https://….plex.direct` URL; some devices do not merely fail on it, they drop their own UPnP control server, which then looks exactly like a device that went offline. `FORCE_HTTP` fixes this, and `PLEX_LAN_ADDRESS` covers controllers that reach Plex over IPv6.
- **The build.** Upstream cannot currently be built from source at all: its base image is unpinned and the pinned dependency wheels no longer compile.
- **Silent failures.** A discovery failure now says why it happened instead of dropping the device, a missing SOAP response is reported instead of being swallowed, and the container no longer runs in a mode that compiles its own error logging out of existence.

## Installation

Docker is the recommended way. **Host networking is required** — UPnP and Plex GDM both need UDP broadcast.

```yaml
services:
  plex-dlna-bridge:
    image: ghcr.io/epheterson/plex-dlna-bridge
    container_name: plex-dlna-bridge
    network_mode: host
    restart: unless-stopped
    volumes:
      - ./config:/config
```

Or directly:

```
docker run -d \
  --name=plex-dlna-bridge \
  --network host \
  --restart unless-stopped \
  -v <path to data>:/config \
  ghcr.io/epheterson/plex-dlna-bridge
```

To run it without Docker, clone the repo and run `main.py` with Python 3.10.

## Setup

Open `http://<host-ip>:32488` and follow the link to pair each renderer with your plex.tv account. Plexamp does not support GDM discovery, so this pairing step is required if you want to use Plexamp as the controller. Plex clients that do support GDM will see your renderers without it.

## Configuration

Configured through [pydantic settings](https://pydantic-docs.helpmanual.io/usage/settings/). Most people need none of these.

| Env | Description | Default |
| :--- | :--- | :--- |
| `HTTP_PORT` | Port for the http server | `32488` |
| `HOST_IP` | IP of this host. Plex clients use `http://HOST_IP:HTTP_PORT` to reach your renderers | auto |
| `ALIASES` | Preferred renderer names, as `uuid:name1,ip:name2,origin_name:name3` | empty |
| `LOCATION_URL` | Description URL of a renderer. Setting this disables auto discovery | none |
| `FORCE_HTTP` | Rewrite Plex's `https://….plex.direct` address to a plain `http://` LAN address, for renderers that cannot fetch HTTPS. Note this applies to all traffic to the Plex server, so the Plex token is sent in cleartext on your LAN, and it will not work if your server requires secure connections | `false` |
| `PLEX_LAN_ADDRESS` | Your Plex server's LAN address, e.g. `192.0.2.10`. Used instead of the plex.direct hostname when `FORCE_HTTP` is on. Needed when the controller reaches Plex over IPv6, since an IPv6 plex.direct name cannot be rewritten on its own | none |
| `CONFIG_PATH` | Where persistent data is stored | `/config` |

Map `/config` to a host directory if you use Plexamp as the controller, or edit device names in the web page — both need to survive a restart.

## Device support

Tested directly against a **Hegel H150**. The fixes here come from real hardware and from the upstream issue tracker, so gear that reports the same symptoms should benefit — Denon/HEOS, Marantz, Oppo and TechniSat all appear in those reports.

This is maintained **best-effort**, by someone with one renderer. Device-specific reports and pull requests are welcome and are the only way support for other hardware gets better. If your renderer misbehaves, the logs are far more useful than they used to be — please include them.

## License and attribution

GPL-3.0, inherited from the original project. This is a modified version of [songchenwen/plexdlnaplayer](https://github.com/songchenwen/plexdlnaplayer); the original commit history and authorship are preserved in this repository's git log. See [CHANGES.md](CHANGES.md) for what has been modified.

Not affiliated with, endorsed by, or sponsored by Plex, Inc. "Plex" and "Plexamp" are trademarks of their respective owner.
