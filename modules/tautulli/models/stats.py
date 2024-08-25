class PlayStatsCategoryData:
    def __init__(self, category_name: str, x_axis: list, values: list):
        self.category_name: str = category_name
        self.x_axis: list = x_axis
        self.values: list = values


class PlayStats:
    def __init__(self, data: dict):
        self._data: dict = data
        self.categories: list = data.get('categories', [])
        self._series: list[dict] = data.get('series', [])

    def _get_category_data(self, category_name: str) -> PlayStatsCategoryData | None:
        raise NotImplementedError

    @property
    def formatted_data(self) -> dict:
        return {
            'tv_shows': self.tv_shows,
            'movies': self.movies,
            'music': self.music
        }

    @property
    def tv_shows(self) -> PlayStatsCategoryData | None:
        return self._get_category_data(category_name='TV')

    @property
    def movies(self) -> PlayStatsCategoryData | None:
        return self._get_category_data(category_name='Movies')

    @property
    def music(self) -> PlayStatsCategoryData | None:
        return self._get_category_data(category_name='Music')


class PlayCountStats(PlayStats):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def _get_category_data(self, category_name: str) -> PlayStatsCategoryData | None:
        for series in self._series:
            if series.get('name', None) == category_name:
                return PlayStatsCategoryData(
                    category_name=category_name,
                    x_axis=self.categories,
                    values=series.get('data', [])
                )

        return None


class PlayDurationStats(PlayStats):
    def __init__(self, data: dict):
        super().__init__(data=data)

    def _get_category_data(self, category_name: str) -> PlayStatsCategoryData | None:
        for series in self._series:
            if series.get('name', None) == category_name:
                return PlayStatsCategoryData(
                    category_name=category_name,
                    x_axis=self.categories,
                    values=series.get('data', [])
                )

        return None
