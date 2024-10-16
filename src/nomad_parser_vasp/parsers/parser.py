from typing import TYPE_CHECKING, Dict, List, Any

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad_parser_vasp.parsers.xml_parser import VASPXMLParser
from nomad_parser_vasp.parsers.outcar_parser import VASPOutcarParser


class VASPParser:
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        is_outcar = 'outcar' in mainfile.lower()

        if is_outcar:
            parser = VASPOutcarParser()

        else:
            parser = VASPXMLParser()
        # TODO remove this for debug
        self.parser = parser
        parser.parse(mainfile, archive, logger, child_archives)
