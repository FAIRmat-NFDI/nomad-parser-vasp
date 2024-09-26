import os
from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.parsing.parser import MatchingParser

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:parser_entry_point'
)


class VASPParser(MatchingParser):
    def parse(
        self, filepath: str, archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> None:
        self.mainfile = filepath
        self.maindir = os.path.dirname(self.mainfile)
        self.basename = os.path.basename(self.mainfile)
        self.archive = archive
