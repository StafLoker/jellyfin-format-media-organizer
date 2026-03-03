<div align="center">
  <img width="150" height="150" src="logo.png" alt="Logo">
  <h1><b>Jellyfin Format Media Organizer</b></h1>
  <p><i>~ JFMO ~</i></p>
  <p align="center">
     <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/releases">Releases</a> ·
     <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/blob/main/LICENSE">License</a>
  </p>
</div>

<div align="center">
  <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/releases"><img src="https://img.shields.io/github/release-pre/StafLoker/jellyfin-format-media-organizer.svg?style=flat" alt="latest version"/></a>
  <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/actions/workflows/ci.yml"><img src="https://github.com/StafLoker/jellyfin-format-media-organizer/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI/CD Build"/></a>
  <a href="https://github.com/StafLoker/jellyfin-format-media-organizer/actions/workflows/ci.yml"><img src="https://github.com/StafLoker/jellyfin-format-media-organizer/actions/workflows/ci.yml/badge.svg?branch=main" alt="Tests"/></a>
  <a href="https://pypi.org/project/jfmo/"><img src="https://img.shields.io/pypi/dm/jfmo?style=flat&label=PyPI%20downloads" alt="PyPI downloads"/></a>
</div>

<br>

Automatically organizes and renames media files according to [Jellyfin's naming conventions](https://jellyfin.org/docs/general/server/media/movies). Detects movies vs TV shows, fetches TMDB metadata, and handles transliteration of non-Latin filenames.

## Features

- Smart movie vs TV show detection
- TMDB integration for IDs and metadata
- Configurable naming via tokens
- **Russian transliteration detection and conversion**
- Daemon mode for continuous monitoring

## Installation

**1. Create a system user and add it to the `media` group:**

```bash
sudo groupadd media
sudo useradd --system --no-create-home --shell /usr/sbin/nologin jfmo
sudo usermod -aG media jfmo
```

Make sure your media directories are owned or readable by the `media` group:

```bash
sudo chown -R :media /data/media
sudo chmod -R g+rw /data/media
```

**2. Set up the config:**

Default config path: `/etc/jfmo/config.yaml`. See [`config.template.yaml`](config.template.yaml) for all options.

```bash
sudo mkdir -p /etc/jfmo
sudo vim /etc/jfmo/config.yaml
sudo chown -R jfmo:jfmo /etc/jfmo
```

### Option 1 — pip / pipx

**3. Install the package:**

```bash
sudo pipx install jfmo --global
```

**4. Create the systemd unit `/etc/systemd/system/jfmo.service`:**

```ini
[Unit]
Description=Jellyfin Format Media Organizer
After=network.target

[Service]
Type=simple
User=jfmo
Group=media
ExecStart=/usr/local/bin/jfmo daemon
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**5. Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jfmo
sudo systemctl status jfmo
```

**Run once manually** (without stopping the daemon):

```bash
sudo -u jfmo -g media jfmo run --apply
```

### Option 2 — Docker

See example of docker compose file in [`docker-compose.template.yaml`](docker-compose.template.yaml).

Set `user` in `docker-compose.yaml` to the `uid:gid` of `jfmo:media` (created above):

```bash
id jfmo                # get uid
getent group media     # get gid
```

**1. Set up files:**

```bash
sudo mkdir -p /opt/jfmo
cd /opt/jfmo
sudo vim docker-compose.yaml
```

Start as a background daemon (restarts automatically on reboot):

```bash
sudo docker compose up -d
```

Run once manually (e.g. to process a backlog):

```bash
# Dry-run preview — no files moved
sudo docker compose run --rm jfmo run

# Apply changes
sudo docker compose run --rm jfmo run --apply
```

## Update

### pipx

```bash
sudo pipx upgrade jfmo --global
sudo systemctl restart jfmo
```

### Docker

```bash
sudo docker compose pull
sudo docker compose up -d
```

## Usage

```
jfmo run              # dry-run preview (no files moved)
jfmo run --apply      # apply changes
jfmo daemon           # watch downloads directory continuously
jfmo --version
```

## Naming

### Available tokens

| Token             | Description                 | Example                     |
| ----------------- | --------------------------- | --------------------------- |
| `{title}`         | Media title                 | `Inception`                 |
| `{year}`          | Release year                | `2010`                      |
| `{tmdb_id}`       | TMDB numeric ID             | `27205`                     |
| `{quality}`       | Resolution label            | `[1080p]`                   |
| `{season}`        | Season number, zero-padded  | `01`                        |
| `{episode}`       | Episode number, zero-padded | `04`                        |
| `{source}`        | Release source              | `WEB-DL`, `BluRay`, `BDRip` |
| `{codec}`         | Video codec                 | `x265`, `HEVC`, `AV1`       |
| `{hdr}`           | HDR format                  | `HDR10`, `DV`, `DoVi`       |
| `{service}`       | Streaming service           | `NF`, `AMZN`, `DSNP`        |
| `{release_group}` | Release group name          | `LostFilm`, `NOOBDL`        |

Each pattern only accepts a specific subset of tokens:

| Pattern (`naming.`) | Allowed tokens                                                                                |
| ------------------- | --------------------------------------------------------------------------------------------- |
| `movie.file`        | `title`, `year`, `tmdb_id`, `quality`, `source`, `codec`, `hdr`, `service`, `release_group`   |
| `tv.folder`         | `title`, `year`, `tmdb_id`                                                                    |
| `tv.season`         | `season`                                                                                      |
| `tv.file`           | `title`, `season`, `episode`, `quality`, `source`, `codec`, `hdr`, `service`, `release_group` |

### Example: before → after

```
downloads/
├── Severance.S02E02.1080p.mkv
├── The.Accountant.2.2024.2160p.mkv
├── Podslushano.v.Rybinske.S01E01.2160p.mkv   ← Russian transliteration
└── La Casa de Papel 3 - LostFilm [1080p]/

films/
└── The Accountant 2 (2024) [tmdbid-717559] - 2160p.mkv

tv/
├── Severance (2022) [tmdbid-95396]/
│   └── Season 02/
│       └── Severance S02E02 - 1080p.mkv
├── Подслушано в Рыбинске (2024) [tmdbid-245083]/   ← converted to Cyrillic
│   └── Season 01/
│       └── Подслушано в Рыбинске S01E01 - 2160p.mkv
└── La Casa de Papel (2017) [tmdbid-71446]/
    └── Season 03/
        └── La Casa de Papel S03E01 - 1080p.mkv
```

## Transliteration Detection

Most media organizers (Radarr, Sonarr, etc.) cannot handle files where the title is written in **Latin-script transliteration of Russian** — e.g. `Podslushano.v.Rybinske.S01.mkv` looks like English but is actually «Подслушано в Рыбинске».

JFMO detects this automatically using a custom **character n-gram language model** trained to distinguish genuine English titles from Russian titles written in transliteration. When a transliterated title is detected, JFMO converts it back to Cyrillic before searching TMDB — resulting in a correct match instead of a failed lookup.

```
Podslushano.v.Rybinske.S01E01.mkv
  detected: Russian transliteration
  converted: Подслушано в Рыбинске
  TMDB match: tmdbid-XXXXXX
  → Подслушано в Рыбинске (2024) [tmdbid-XXXXXX]/Season 01/...
```

The model was trained on a custom dataset of ~2.5M titles (165k Russian + 2.4M English) built specifically for this project, achieving **93% accuracy** on a diverse test set of 334 cases.

- Dataset: [stafloker/media-transliterated](https://www.kaggle.com/datasets/stafloker/media-transliterated) (Kaggle)
- Inspired by: [Language Identification for Texts Written in Transliteration](https://ceur-ws.org/Vol-871/paper_2.pdf)

## Acknowledgments

- [Jellyfin](https://jellyfin.org/) · [TMDB](https://www.themoviedb.org/) · [transliterate](https://pypi.org/project/transliterate/)
