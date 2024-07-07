from nomad.datamodel.datamodel import (
    EntryArchive,
)
from structlog.stdlib import (
    BoundLogger,
)

from nomad.config import config
from nomad.parsing import MatchingParser
from nomad.parsing.file_parser.xml_parser import XMLParser

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:xml_entry_point'
)


class VasprunXMLParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] = None,
    ) -> None:
        logger.info('VasprunXMLParser.parse', parameter=configuration.parameter)
        xml_reader = XMLParser(mainfile=mainfile).parse('/*')  # XPath syntax
        archive.data = xml_reader._results
