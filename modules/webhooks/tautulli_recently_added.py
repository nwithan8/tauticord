import json
from typing import Union, Optional

from pydantic import Field, BaseModel
from tautulli.tools.webhooks import TautulliWebhook, TautulliWebhookTrigger


class RecentlyAddedWebhookData(BaseModel):
    """
    Data from a configured webhook for recently added media
    """
    media_type: Optional[str] = None
    library_name: Optional[str] = None
    title: Optional[str] = None
    year_: Optional[str] = Field(None, alias='year')
    duration_: Optional[str] = Field(None, alias='duration')
    tagline: Optional[str] = None
    summary: Optional[str] = None
    studio: Optional[str] = None
    directors_: Optional[str] = Field(None, alias='directors')
    actors_: Optional[str] = Field(None, alias='actors')
    genres_: Optional[str] = Field(None, alias='genres')
    plex_id: Optional[str] = None
    critic_rating_: Optional[str] = Field(None, alias='critic_rating')
    audience_rating_: Optional[str] = Field(None, alias='audience_rating')
    poster_url: Optional[str] = None

    @property
    def year(self) -> Union[int, None]:
        return int(self.year_) if self.year_ else None

    @property
    def duration(self) -> Union[int, None]:
        """
        Get the duration of the media in minutes
        """
        if not self.duration_:
            return None

        if ':' not in self.duration_:
            return int(self.duration_)

        hours, minutes = self.duration_.split(':')
        return int(hours) * 60 + int(minutes)

    @property
    def directors(self) -> list[str]:
        return self.directors_.split(', ') if self.directors_ else []

    @property
    def actors(self) -> list[str]:
        return self.actors_.split(', ') if self.actors_ else []

    @property
    def genres(self) -> list[str]:
        return self.genres_.split(', ') if self.genres_ else []

    @property
    def critic_rating(self) -> Union[float, None]:
        return float(self.critic_rating_) if self.critic_rating_ else None

    @property
    def audience_rating(self) -> Union[float, None]:
        return float(self.audience_rating_) if self.audience_rating_ else None


# ref: https://github.com/Tautulli/Tautulli/blob/d019efcf911b4806618761c2da48bab7d04031ec/plexpy/notifiers.py#L1148
class RecentlyAddedWebhook(TautulliWebhook):
    """
    A recently-added webhook from Tautulli
    """
    data: RecentlyAddedWebhookData

    @classmethod
    def from_flask_request(cls, request) -> Union["RecentlyAddedWebhook", None]:
        """
        Ingest a configured recently-added webhook from a Flask request

        :param request: The incoming Flask request
        :return: The processed recently-added webhook, or None if the request could not be processed
        """
        try:
            body = request.get_json()
        except Exception:
            # JSON data is stored in the form field 'payload_json' if files are present
            # ref: https://github.com/Tautulli/Tautulli/blob/d019efcf911b4806618761c2da48bab7d04031ec/plexpy/notifiers.py#L1225
            body = json.loads(request.form.get('payload_json', '{}'))

        if not body:
            return None

        data = RecentlyAddedWebhookData(**body)
        if not data or not data.title:
            return None

        return cls(data=data)

    def _determine_trigger(self, **kwargs: dict) -> Union[TautulliWebhookTrigger, None]:
        return TautulliWebhookTrigger.RECENTLY_ADDED
