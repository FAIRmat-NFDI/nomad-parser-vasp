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
from nomad.parsing.file_parser.mapping_parser import (
    MetainfoParser,
    XMLParser,
)
from nomad_parser_vasp.schema_packages.vasp_package import Simulation

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:xml_entry_point'
)

mix_alpha = lambda mix, cond: mix if cond else 0  # pylint: disable=W0613


class VasprunXMLParser:
    def parse(
        self,
        mainfile: 'str',
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: 'dict[str, EntryArchive]' = None,
    ) -> None:
        logger.info(self.__class__.__name__, parameter=configuration.parameter)

        data_parser = MetainfoParser(annotation_key='xml', data_object=Simulation())
        XMLParser(filepath=mainfile).convert(data_parser)
        archive.data = data_parser.data_object
