from nomad.datamodel.datamodel import (
    EntryArchive,
)
from structlog.stdlib import (
    BoundLogger,
)

from nomad.config import config
from nomad.parsing import MatchingParser
from nomad.parsing.file_parser.mapping_parser import (
    MetainfoParser,
    XMLParser,
)
from schema_packages.vasp_package import Simulation

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
        data_parser = MetainfoParser(annotation_key='xml', data_object=Simulation())
        XMLParser(filepath=mainfile).convert(data_parser)
        archive.data = data_parser.data_object
