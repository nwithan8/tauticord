from modules.database.base.imports import *


class Version(Base):
    __tablename__ = 'version'
    semver = Column("semver", String, primary_key=True, nullable=False)

    def __init__(self, semver: str, **kwargs):
        self.semver = semver
