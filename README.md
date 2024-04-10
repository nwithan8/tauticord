<div align="center">

# Tauticord

A Discord bot that displays live data from Tautulli

[![Release](https://img.shields.io/github/v/release/nwithan8/tauticord?color=yellow&include_prereleases&label=version&style=flat-square)](https://github.com/nwithan8/tauticord/releases)
[![Docker](https://img.shields.io/docker/pulls/nwithan8/tauticord?style=flat-square)](https://hub.docker.com/r/nwithan8/tauticord)
[![Licence](https://img.shields.io/github/license/nwithan8/tauticord?style=flat-square)](https://opensource.org/licenses/GPL-3.0)

<a href="https://www.buymeacoffee.com/nwithan8" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="19" width="95"></a>
[![GitHub Sponsors](https://img.shields.io/github/sponsors/nwithan8?style=flat-square)](https://github.com/sponsors/nwithan8)

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/logo.png" alt="logo">

</div>

# Features ⚙️

Tauticord uses the Tautulli API to pull information from Tautulli and display them in a Discord channel, including:

### Overview:

* Number of current streams
* Number of transcoding streams
* Total bandwidth
* Total LAN bandwidth
* Total remote bandwidth
* Library item counts

### For each stream:

* Stream state (playing, paused, stopped, loading)
* Media type (tv show/movie/song/photo)
* User
* Media title
* Product and player
* Quality profile
* Stream bandwidth
* If stream is transcoding
* Progress of stream
* ETA of stream completion

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/embed.png">

Administrator (the bot owner) can react to Tauticord's messages to terminate a specific stream (if they have Plex Pass).

Users can also indicate what libraries they would like monitored. Tauticord will create/update a voice channel for each
library name with item counts every hour.

<img src="https://raw.githubusercontent.com/nwithan8/tauticord/master/documentation/images/libraries.png">

# Announcements 📢

See [ANNOUNCEMENTS](documentation/ANNOUNCEMENTS.md).

# Documentation 📄

See [DOCUMENTATION](documentation/DOCUMENTATION.md).

# Development 🛠️

See [DEVELOPMENT](documentation/DEVELOPMENT.md).

# Contact 📧

Please leave a pull request if you would like to contribute.

Also feel free to check out my other projects here on [GitHub](https://github.com/nwithan8) or join the `#developer`
channel in my Discord server below.

<div align="center">
	<p>
		<a href="https://discord.gg/ygRDVE9"><img src="https://discordapp.com/api/guilds/472537215457689601/widget.png?style=banner2" alt="" /></a>
	</p>
</div>

## Shout-outs 🎉

### Sponsors

[![JetBrains](https://avatars.githubusercontent.com/u/60931315?s=120&v=4)](https://github.com/JetBrainsOfficial)

<!-- github-sponsors --><a href="https://github.com/upamanyudas"><img src="https://github.com/upamanyudas.png" width="80px" alt="upamanyudas" /></a>&nbsp;&nbsp;<a href="https://github.com/l33xu"><img src="https://github.com/l33xu.png" width="80px" alt="l33xu" /></a>&nbsp;&nbsp;<!-- github-sponsors -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

### Contributors

<table>
<tr>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/nwithan8>
            <img src=https://avatars.githubusercontent.com/u/17054780?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Nate Harris/>
            <br />
            <sub style="font-size:14px"><b>Nate Harris</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/TomW1605>
            <img src=https://avatars.githubusercontent.com/u/17092573?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Thomas White/>
            <br />
            <sub style="font-size:14px"><b>Thomas White</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/twilsonco>
            <img src=https://avatars.githubusercontent.com/u/7284371?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Tim Wilson/>
            <br />
            <sub style="font-size:14px"><b>Tim Wilson</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/benwaco>
            <img src=https://avatars.githubusercontent.com/u/127471645?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Ben Waco/>
            <br />
            <sub style="font-size:14px"><b>Ben Waco</b></sub>
        </a>
    </td>
</tr>
<tr>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/tdurieux>
            <img src=https://avatars.githubusercontent.com/u/5577568?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Thomas Durieux/>
            <br />
            <sub style="font-size:14px"><b>Thomas Durieux</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 75.0; height: 75.0">
        <a href=https://github.com/Yoruio>
            <img src=https://avatars.githubusercontent.com/u/38411921?v=4 width="50;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Roy Du/>
            <br />
            <sub style="font-size:14px"><b>Roy Du</b></sub>
        </a>
    </td>
</tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
