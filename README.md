# Plex DLNA Bridge

Cast Plex and Plexamp to any UPnP/DLNA renderer — an amplifier, a network streamer, a pair of active speakers — in **bit-perfect quality**.

Your renderer shows up in Plex's `Select Player` window and Plexamp's output list, then fetches the original file straight from your Plex server — so a 24-bit FLAC arrives untouched. AirPlay caps at 16/44.1 and Chromecast re-encodes; this doesn't.

Based on [songchenwen/plexdlnaplayer](https://github.com/songchenwen/plexdlnaplayer), which has had no commits since 2021. These changes are also open upstream as [#25](https://github.com/songchenwen/plexdlnaplayer/pull/25).

## What's different

- **Renderers advertising v2 UPnP services** (`AVTransport:2` / `RenderingControl:2`) are supported — common on modern amplifiers, including Hegel and other Rygel-based stacks. Previously they weren't recognised, and position, volume and transport state came back empty.
- **Devices sending an empty or whitespace `<modelDescription/>`** now pair correctly (upstream [#22](https://github.com/songchenwen/plexdlnaplayer/issues/22), [#14](https://github.com/songchenwen/plexdlnaplayer/pull/14)).
- **Errors from a device** surface the actual HTTP status instead of an `AttributeError` (upstream [#18](https://github.com/songchenwen/plexdlnaplayer/issues/18)).
- **`FORCE_HTTP` / `PLEX_LAN_ADDRESS`** for renderers that can't fetch HTTPS — some drop their UPnP control server entirely when handed a TLS URL, which looks like the device going offline.
- **Builds from source again** — base image pinned to `python:3.10`, and the CI workflow updated to current action versions.
- **Clearer logs** — discovery failures say why, and an unparsed SOAP response is reported rather than returning empty state.

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
| `ONLY_DEVICES` | Register only these renderers, as `uuid,name,ip` — matched the same way as `ALIASES`. Empty means all | empty |
| `IGNORE_DEVICES` | Never register these renderers, same format. Useful when your network has speakers you don't want cluttering Plex's player list | empty |
| `FORCE_HTTP` | Rewrite Plex's `https://….plex.direct` address to a plain `http://` LAN address, for renderers that cannot fetch HTTPS. Note this applies to all traffic to the Plex server, so the Plex token is sent in cleartext on your LAN, and it will not work if your server requires secure connections | `false` |
| `PLEX_LAN_ADDRESS` | Your Plex server's LAN address, e.g. `192.0.2.10`. Used instead of the plex.direct hostname when `FORCE_HTTP` is on. Needed when the controller reaches Plex over IPv6, since an IPv6 plex.direct name cannot be rewritten on its own | none |
| `CONFIG_PATH` | Where persistent data is stored | `/config` |

Map `/config` to a host directory if you use Plexamp as the controller, or edit device names in the web page — both need to survive a restart.

## Device support

Tested against a **Hegel H150**. The other fixes come from the upstream issue tracker, where Denon/HEOS, Marantz, Oppo and TechniSat owners reported the same symptoms.

Maintained best-effort with one renderer to test on. Device reports and PRs welcome — please include logs.

## License and attribution

GPL-3.0, same as the original. Modified version of [songchenwen/plexdlnaplayer](https://github.com/songchenwen/plexdlnaplayer) — original commit history and authorship are preserved in the git log, changes listed in [CHANGES.md](CHANGES.md).

Not affiliated with Plex, Inc.
