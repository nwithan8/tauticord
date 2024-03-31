# Migrating from v4.x.x to v5.x.x

Version 5.0.0 of Tauticord introduces major changes, including:

- A major change to the structure (schema) of the configuration (YAML) file
- Configuration file renamed from `config.yaml`to `tauticord.yaml`
- Dropped support for configuration via environmental variables

This guide details the differences between the config file used in v4.x.x and earlier and the new version using in
v5.x.x.

> :pencil2: **v4.2.x and v5.x.x of Tauticord ship with built-in tools that will automatically migrate configuration
files as needed**

> :warning: **Unraid users, please see ["Migrating on Unraid"](#warning-migrating-on-unraid)**

## New Configuration File

The schema for the configuration file has been changed to improve readability and logical grouping of settings, make it
easier to set up libraries and combined libraries, and allow per-channel customization for each statistic/metric voice
channel.

The following is a list of previous configuration variable paths in `config.yaml` and their corresponding new location
in `tauticord.yaml`:

```diff
- Tautulli -> Connection -> URL
+ Tautulli -> URL
```

```diff
- Tautulli -> Connection -> APIKey
+ Tautulli -> APIKey
```

```diff
- Tautulli -> Connection -> UseSelfSignedCert
+ Tautulli -> UseSelfSignedCert
```

```diff
- Tautulli -> Customization -> ServerName
+ Display -> ServerName
```

```diff
- Tautulli -> Customization -> TerminateMessage
+ Tautulli -> TerminateMessage
```

```diff
- Tautulli -> Customization -> RefreshSeconds
+ Tautulli -> RefreshSeconds
```

```diff
- Tautulli -> Customization -> PlexPass
+ <none>
```

```diff
- Tautulli -> Customization -> ServerTimeZone
+ Display -> Time -> ServerTimeZone
```

```diff
- Tautulli -> Customization -> Use24HourTime
+ Display -> Time -> Use24HourTime
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> CategoryName
+ Stats -> Activity -> CategoryName
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> StreamCount
+ Stats -> Activity -> StatTypes -> StreamCount -> Enable
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> StreamCountChannelID
+ Stats -> Activity -> StatTypes -> StreamCount -> VoiceChannelID
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> TranscodeCount
+ Stats -> Activity -> StatTypes -> TranscodeCount -> Enable
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> TranscodeCountChannelID
+ Stats -> Activity -> StatTypes -> TranscodeCount -> VoiceChannelID
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> Bandwidth
+ Stats -> Activity -> StatTypes -> Bandwidth -> Enable
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> BandwidthChannelID
+ Stats -> Activity -> StatTypes -> Bandwidth -> VoiceChannelID
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> LocalBandwidth
+ Stats -> Activity -> StatTypes -> LocalBandwidth -> Enable
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> LocalBandwidthChannelID
+ Stats -> Activity -> StatTypes -> LocalBandwidth -> VoiceChannelID
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> RemoteBandwidth
+ Stats -> Activity -> StatTypes -> RemoteBandwidth -> Enable
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> RemoteBandwidthChannelID
+ Stats -> Activity -> StatTypes -> RemoteBandwidth -> VoiceChannelID
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> PlexStatus
+ Stats -> Activity -> StatTypes -> PlexServerAvailability -> Enable
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Stats -> PlexStatusChannelID
+ Stats -> Activity -> StatTypes -> PlexServerAvailability -> VoiceChannelID
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> CategoryName
+ Stats -> Libraries -> CategoryName
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> Enable
+ Stats -> Libraries -> Enable
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> LibraryRefreshSeconds
+ Stats -> Libraries -> RefreshSeconds
```

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> LibraryNames
```

See [Libraries configuration](../DOCUMENTATION.md#libraries)

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> CombinedLibraries
```

See [Combined Libraries configuration](../DOCUMENTATION.md#combined-libraries)

```diff

- Tautulli -> Customization -> VoiceChannels -> Libraries -> UseEmojis
```

See [Voice Channel Customization](../DOCUMENTATION.md#voice-channel-customization)

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> TVSeriesCount
```

See [Libraries configuration](../DOCUMENTATION.md#libraries)

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> TVEpisodeCount
```

See [Libraries configuration](../DOCUMENTATION.md#libraries)

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> MusicArtistCount
```

See [Libraries configuration](../DOCUMENTATION.md#libraries)

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> MusicAlbumCount
```

See [Libraries configuration](../DOCUMENTATION.md#libraries)

```diff
- Tautulli -> Customization -> VoiceChannels -> Libraries -> MusicTrackCount
```

See [Libraries Configuration](#library-configuration)

```diff
- Tautulli -> Customization -> VoiceChannels -> Performance -> CategoryName
+ Stats -> Performance -> CategoryName
```

```diff
- Tautulli -> Customization -> Anonymize -> HideUsernames
+ Display -> Anonymize -> HideUsernames
```

```diff
- Tautulli -> Customization -> Anonymize -> HidePlayerNames
+ Display -> Anonymize -> HidePlayerNames
```

```diff
- Tautulli -> Customization -> Anonymize -> HidePlatforms
+ Display -> Anonymize -> HidePlatforms
```

```diff
- Tautulli -> Customization -> Anonymize -> HideQuality
+ Display -> Anonymize -> HideQuality
```

```diff
- Tautulli -> Customization -> Anonymize -> HideBandwidth
+ Display -> Anonymize -> HideBandwidth
```

```diff
- Tautulli -> Customization -> Anonymize -> HideTranscode
+ Display -> Anonymize -> HideTranscode
```

```diff
- Tautulli -> Customization -> Anonymize -> HideProgress
+ Display -> Anonymize -> HideProgress
```

```diff
- Tautulli -> Customization -> Anonymize -> HideETA
+ Display -> Anonymize -> HideETA
```

```diff
- Tautulli -> Customization -> UseFriendlyNames
+ Display -> UseFriendlyNames
```

```diff
- Tautulli -> Customization -> ThousandSeparator
+ Display -> ThousandSeparator
```

```diff
- Discord -> Connection -> BotToken
+ Discord -> BotToken
```

```diff
- Discord -> Connection -> ServerID
+ Discord -> ServerID
```

```diff
- Discord -> Connection -> AdminIDs
+ Discord -> AdminIDs
```

```diff
- Discord -> Connection -> PostSummaryMessage
+ Discord -> PostSummaryMessage
```

```diff
- Discord -> Connection -> ChannelName
+ Discord -> ChannelName
```

```diff
- Discord -> Connection -> EnableSlashCommands
+ Discord -> EnableSlashCommands
```

```diff
- Discord -> Customization -> Nitro
+ <none>
```

```diff
- Extras -> Analytics
+ Extras -> AllowAnalytics
```

```diff
- Extras -> Performance -> TautulliUserCount
+ Stats -> Performance -> Metrics -> UserCount -> Enable
```

```diff
- Extras -> Performance -> DiskSpace
+ Stats -> Performance -> Metrics -> DiskSpace -> Enable
```

```diff
- Extras -> Performance -> CPU
+ Stats -> Performance -> Metrics -> CPU -> Enable
```

```diff
- Extras -> Performance -> Memory
+ Stats -> Performance -> Metrics -> Memory -> Enable
```

Additional settings have been added to the configuration file. Please refer to the comments in `tauticord.yaml.example`
and the provided [configuration schema](../DOCUMENTATION.md#configuration-schema) for more information.

## :warning: Migrating on Unraid

Starting with v5.0.0, the Unraid Community Application template for Tauticord no longer provides environmental
variable (Variable) configuration options. As a result, you will not be able to provide environmental variables to
configure Tauticord from the Unraid web UI.

The new template will be pulled in automatically when the Community Applications plugin is updated on your
Unraid machine. Unless you manually avoid updating the plugin, the new template will likely be imported into your
system.

Unraid users have two options:

- Manually migrate their environmental variables to the `tauticord.yaml` configuration file
    - **Note**: Your previously-configured Variables may not be visible in the GUI to reference due to the template
      change. If so, **DO NOT** save any changes to your container configuration and exit the GUI.
    - You can attempt to "rescue" the old configuration layout, which should be stored
      in `/boot/config/plugins/dockerMan/templates-user/my-Tauticord.xml` on your Unraid machine. Simply view/download
      the file from your server for referencing.
- [Step-increment your Docker container](#how-to-step-increment-in-unraid)

#### How to step-increment in Unraid

Step-incrementing the Docker container on Unraid will leverage Tauticord's built-in configuration migration tools, by
first migrating existing environmental variables to a config file (v4.x.x) and then converting that config file to the
new schema (v5.x.x).

Please follow the following steps:

1. **DO NOT** open the GUI configuration editor for your Tauticord container. If the Community Applications plugin has
   updated on your system and the new template has been imported, it could interfere with this step-incrementing
   process.
2. Delete your existing Tauticord container from the Docker tab in your Unraid web UI (yes, really).
3. Download your existing Tauticord configuration template file (stored
   at `/boot/config/plugins/dockerMan/templates-user/my-Tauticord.xml` on your Unraid system) to a separate
   folder/machine for safe keeping.
4. Copy your existing Tauticord configuration template file (see above)
   to `/boot/config/plugins/dockerMan/templates/tauticord_v4.xml`.
   This folder stores templates separate from those provided by the Community Applications plugin.
5. Edit the Tauticord configuration template (`/boot/config/plugins/dockerMan/templates/tauticord_v4.xml`) and change:
    ```diff
    - <Repository>nwithan8/tauticord:latest</Repository>
    + <Repository>nwithan8/tauticord:4.2.2</Repository>
    ```
6. Open the Docker tab in your Unraid web UI, and click "Add Container" at the bottom of the page.
7. From the "Template" dropdown, select "Tauticord" from the "Default templates" section (not from the "User templates"
   section). Your previous configuration should populate on the page.
8. Verify that your configuration is correct. Toggle "Advanced View" in the top-right corner of the page and confirm
   that the "Repository" is "nwithan8/tauticord:4.2.2"
9. Click "Apply" at the bottom of the screen. Tauticord v4.2.2 should now be running on your system.
10. Wait a few minutes for Tauticord to start up and complete the migration process. You can verify this process by
    clicking on the icon next to the running container and selecting "Logs" from the dropdown. The log file should
    say `Migration 001: Copying environment variables to /config/migration_data/001_env_var_to_config_yaml.yaml`
    followed by normal bot operation.
11. The migration of environmental variables to a configuration file is now complete. Shut down and delete the Tauticord
    container.
12. Open the Community Applications store in the Unraid web UI and search for "Tauticord". Click "Install".
13. You are now installing/configuring v5.x.x of Tauticord. Notice the lack of Variables to configure. Use the
    same `Config Path`, `Log Path` and `Monitor Path` settings as before. This is crucial, as the migration files
    created in the previous steps exist in whatever path was mapped to `/config`, so `/config` needs to be mapped to the
    same path for migration to complete properly.
14. Verify that your configuration is correct. Toggle "Advanced View" in the top-right corner of the page and confirm
    that the "Repository" is "nwithan8/tauticord:latest"
15. Click "Apply" at the bottom of the screen. Tauticord v5.x.x should now be running on your system.
16. Wait a few minutes for Tauticord to start up and complete the migration process. You can verify this process by
    clicking on the icon next to the running container and selecting "Logs" from the dropdown. The log file should
    say `Migration 002: Migrating old config to new config schema`. The bot (not the Docker container) will restart
    itself automatically following the migration.
17. Enjoy Tauticord!
