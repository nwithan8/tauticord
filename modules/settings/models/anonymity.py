from modules.settings.models.base import BaseConfig


class Anonymity(BaseConfig):
    hide_bandwidth: bool
    hide_eta: bool
    hide_platforms: bool
    hide_player_names: bool
    hide_progress: bool
    hide_quality: bool
    hide_transcode_decision: bool
    hide_usernames: bool

    def as_dict(self) -> dict:
        return {
            "hide_bandwidth": self.hide_bandwidth,
            "hide_eta": self.hide_eta,
            "hide_platforms": self.hide_platforms,
            "hide_player_names": self.hide_player_names,
            "hide_progress": self.hide_progress,
            "hide_quality": self.hide_quality
        }
