from modules.settings.models.base import BaseConfig

from modules.settings.models.voice_category import ActivityStats, LibraryStats, PerformanceStats


class Stats(BaseConfig):
    activity: ActivityStats
    library: LibraryStats
    performance: PerformanceStats

    def as_dict(self) -> dict:
        return {
            "activity": self.activity.as_dict(),
            "library": self.library.as_dict(),
            "performance": self.performance.as_dict()
        }
