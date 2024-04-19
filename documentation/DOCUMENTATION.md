# Installation and setup

## Compatibility

Tauticord is compatible with the following versions of Tautulli:
- v2.12.x
- v2.13.x

## Requirements

- A Plex Media Server
- Tautulli (formerly known as PlexPy)
- A Discord server
- Docker
- [A Discord bot token](https://www.digitaltrends.com/gaming/how-to-make-a-discord-bot/)
    - Permissions required:

      <img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/permissions.png" alt="permissions">

      **SHORTCUT**: Discord occasionally changes the name of some permissions, so the screenshot above may be outdated.
      However, the final "Permissions Integer" won't change; you can use the following link to invite your bot to your
      server with the correct permissions:
      https://discord.com/oauth2/authorize?client_id=YOUR_APPLICATION_ID&scope=bot&permissions=3222350928
        - You will also need to enable "Message Content Intent" [in the bot settings in the Discord Developer Portal]()
          to allow [slash commands](#commands) to work. **This is required regardless of whether you have slash commands
          enabled.**

      <img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/message_content_intent.png">

Tauticord runs as a Docker container. The Dockerfile is included in this repository, or can be pulled
from [Docker Hub](https://hub.docker.com/r/nwithan8/tauticord)
or [GitHub Packages](https://github.com/nwithan8/tauticord/pkgs/container/tauticord).

### Volumes

You will need to map the following volumes:

| Host Path                 | Container Path | Reason                                                                                   |
|---------------------------|----------------|------------------------------------------------------------------------------------------|
| /path/to/logs/folder      | /logs          | Required, debug log file for bot will be generated here                                  |
| /path/to/config/folder    | /config        | Optional, path to the folder containing the configuration file                           |
| /path/to/monitored/folder | /monitor       | Optional, path to a folder to monitor for disk usage statistics (e.g. your Plex library) |

## Configuration

1. Map the `/config` directory (see volumes above)
2. Enter the mapped directory on your host machine
3. Rename the ``tauticord.yaml.example`` file in the path to ``tauticord.yaml``
4. Complete the variables in ``tauticord.yaml``

The example configuration file is commented to help you understand what each variable does. All variables are required,
so please complete the file in its entirety.

#### Configuration Schema

If you are using an IDE with support
for [YAML validation ](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) or JSON Schema Store, the
file should automatically import and begin validating against the schema. Hovering over elements in the configuration
file should provide additional documentation. The schema is
available [here](https://raw.githubusercontent.com/nwithan8/tauticord/master/.schema/config_v2.schema.json).

### Special Configuration Notes

- Discord:
    - [Slash Commands](#commands) require the `Message Content Intent` to be enabled in the Discord Developer Portal.
- [Stats (Voice Channels)](#stats-voice-channels)
    - [Voice Channel Customization](#voice-channel-customization)
    - [Activity Statistics](#activity-statistics)
    - [Library Statistics](#library-statistics)
        - [Libraries](#libraries)
        - [Combined Libraries](#combined-libraries)
    - [Performance Monitoring](#performance-monitoring)
        - [System Access](#system-access)
            - [Disk Space Monitoring](#disk-space-monitoring)
- Extras
    - [Analytics](#analytics)

### Run Command

With Docker installed, run the following command to start Tauticord:

```shell
docker run -d \
  --name tauticord \
  -v /path/to/logs/folder:/logs \
  -v /path/to/config/folder:/config \
  nwithan8/tauticord:latest
```

Using Docker Compose:

```shell
docker-compose -f /path/to/your/docker-compose.yml up -d
```

## Run without Docker

Tauticord only runs as a Docker container. No other methods of running Tauticord are officially supported.

# Stats (Voice Channels)

Tauticord currently offers three different types of statistics to display in voice channels:

- [Activity Statistics](#activity-statistics)
- [Library Statistics](#library-statistics)
- [Performance Monitoring](#performance-monitoring)

### Voice Channel Customization

All statistic voice channels have the following customization options:

- Enable/Disable the voice channel (if disabled, Tauticord will not create/update the channel)
- Custom name (overrides the default name for the statistic)
- Custom emoji (overrides the default emoji for the statistic)
- Voice channel ID specification (rather than letting Tauticord auto-generate the channel)

## Activity Statistics

Activity statistics are about live activity taking place on the Plex server. This includes:

- Current stream count
- Current transcode count
- Current local bandwidth
- Current remote bandwidth
- Current total bandwidth
- Plex Server availability

Activity statistics can be enabled/disabled wholesale, or on
an [individual channel basis](#voice-channel-customization).

Activity statistics update at the same rate as the summary message (with a minimum of 5 seconds between updates).

## Library Statistics

Library statistics are about the media stored on the Plex server. This includes (per library):

- Total movie count
- Total show/series count
- Total episode count
- Total music artist count
- Total album count
- Total song/track count

Only metrics relevant to the library type will be displayed. For example, a music library will not display a movie
count, and a movie library will not display an album count.

Library statistics can be enabled/disabled wholesale, or on an [individual channel basis](#voice-channel-customization).

### Libraries

To display library statistics, you must specify the libraries you want to display in the `Libraries` section of the
`tauticord.yaml` file.

```yaml
Libraries:
  # List of libraries to display statistics for
  - Name: Audiobooks  # The name of the library in Plex
    AlternateName: My Audiobooks  # The name to display in the statistics voice channels
    Albums: # Settings for the "Albums" statistic
      CustomName: 'Books'  # Custom name to use for the statistic
      CustomEmoji: '📻'  # Custom emoji to use for the statistic
      Enable: true
      VoiceChannelID: 0  # The ID of the voice channel to update (0 for auto-management)
    Artists: # Settings for the "Artists" statistic
      ...
    Episodes: # Settings for the "Episodes" statistic
      ...
    Movies: # Settings for the "Movies" statistic
      ...
    Series: # Settings for the "Series" statistic
      ...
    Tracks: # Settings for the "Tracks" statistic
      ...
  - Name: Movies
    AlternateName: My Movies
    Albums:
      ...
    Artists:
      ...
    Episodes:
      ...
    Movies:
      ...
    Series:
      ...
    Tracks:
      ...
```

Library data updates at a configurable interval (with a minimum of 5 minutes between updates).

### Combined Libraries

You can optionally combine multiple Plex libraries into one for display in the voice channel. This is useful if you have
multiple "movies" libraries, for example, and you want to display them all as one in terms of statistics.

To do this, you must specify the libraries you want to combine in the `CombinedLibraries` section of
the `tauticord.yaml`
file.

```yaml
CombinedLibraries:
  # List of combined libraries to display statistics for
  - Name: My Combined Movies  # The name of the combined library
    Libraries: # List of libraries to combine
      - Movies
      - Movies (4K)
      - Movies (Foreign)
    Albums:
      ...
    Artists:
      ...
    Episodes:
      ...
    Movies:
      ...
    Series:
      ...
    Tracks:
      ...
```

Combined library data updates at the same interval as regular library data (with a minimum of 5 minutes between
updates).

## Performance Monitoring

Performance monitoring will report metrics such as:

- CPU usage
- RAM usage
- Disk space usage
- Plex user count

Performance monitoring can be enabled/disabled wholesale, or on
an [individual channel basis](#voice-channel-customization).

Tauticord will attempt to query the system it is running on for these metrics every 5 minutes (non-configurable).

### System Access

Tautulli does not currently offer a way to query performance statistics from its API. As a result, this data is **not
Tautulli-specific performance data**, but rather **the performance of the system that Tauticord is running on**.

If Tauticord is running on the same system as Tautulli, then this data may reflect the performance of Tautulli (+
Tauticord and all other processes running on the system).

If Tauticord is running on a different system than Tautulli, or is running isolated in a Docker container, then this
data will not reflect the performance of Tautulli.

#### Disk Space Monitoring

Tauticord's disk space monitoring feature will analyze the used and total space of the provided folder (default: The
path mounted to `/monitor` inside the Docker container). This feature can be used, for example, to monitor the disk
space of your Plex library, as long as the path to the library is mounted to `/monitor`. This will not work if Tauticord
is running on a separate system from the Plex library.

# Commands

Out of the box, Tauticord does mostly passive, non-interactive things (posting messages, updating voice channels, etc.).

However, Tauticord also has a few commands that can be used to interact with it, via Discord's slash commands. Below is
a non-exhaustive list of commands that Tauticord supports:

### `/recently-added`

**Any user can use this command.**

Displays the most recently added media to the Plex server.

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/recently_added.png" alt="recently_added">

### `/most popular-movies`

**This command and its variants are locked to administrators only.**

Displays the most popular movies on the Plex server. This is similar to the "Most X" sections on the Tautulli homepage.

Variants:

- `/most popular-movies`
- `/most popular-shows`
- `/most popular-artists`
- `/most watched-movies`
- `/most watched-shows`
- `/most played-artists`
- `/most active-users`
- `/most active-platforms`
- `/most active-libraries`

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/most_active_libraries.png" alt="most_active_libraries">

### `/summary`

**This command is locked to administrators only.**

Displays a summary of the current Tautulli statistics. This is the exact same summary that Tauticord automatically
posts.

All slash command responses are ephemeral (only visible to the user who triggered it) by default. Most slash commands,
however, have a `share` option that can be used to make the response visible to everyone in the channel.

# Common Issues

- On startup, Tauticord attempts to upload a set of custom emojis that it will use when displaying stream information (
  if they do not already exist). Your bot will need to have the `Manage Emojis` permission in order to do this.
    - Discord has a limit of 50 custom emojis per server. If you have reached this limit, you will need to remove some
      of your existing emojis before Tauticord can upload its own.
    - If you do not want to remove any of your existing emojis, Tauticord will simply skip uploading its own emojis and
      use the default emojis that Discord provides instead.

# Analytics

Tauticord uses Google Analytics to collect statistics such as common errors that will help with future development.
**This data is limited, anonymous, and never sold or redistributed.**

**When and what data is collected?**

- Whenever the bot comes online
    - What operating system the bot is running on (Windows, Linux, MacOS, etc.)
- Whenever an error is logged
    - What function the error occurred in.

**What data is NOT collected:**

- Any identifying information about the user
- Any identifying information about the computer/machine (a random ID is generated on each analytics call, IP addresses
  are anonymized)
- Settings for Discord or Tautulli, including passwords, API tokens, URLs, etc.
- Any data from Tautulli
- Anything typed in Discord.
