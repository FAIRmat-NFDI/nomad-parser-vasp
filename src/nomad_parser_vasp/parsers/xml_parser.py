from typing import TYPE_CHECKING, Any, Dict, List

import numpy as np

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.parsing.file_parser.mapping_parser import MetainfoParser, Path, XMLParser
from nomad_simulations.schema_packages.general import Simulation

from nomad_parser_vasp.schema_packages.vasp_package import (
    XML2_ANNOTATION_KEY,
    XML_ANNOTATION_KEY,
)

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:vasp_parser_entry_point'
)


class VasprunParser(XMLParser):
    def mix_alpha(self, mix: float, cond: bool) -> float:
        return mix if cond else 0

    def get_eigenvalues(self, array: list) -> Dict[str, Any]:
        if array is None:
            return {}
        transposed = np.transpose(array)
        return dict(eigenvalues=transposed[0], occupations=transposed[1])

    def get_energy_contributions(
        self, source: Dict[str, Any], **kwargs
    ) -> List[Dict[str, Any]]:
        return [
            c
            for c in source
            if c.get(f'{self.attribute_prefix}name') not in kwargs.get('exclude', [])
        ]

    def get_data(self, source: Dict[str, Any], **kwargs) -> Any:
        if source.get(self.value_key):
            return source[self.value_key]
        path = kwargs.get('path')
        if path is None:
            return

        parser = Path(path=path)
        return parser.get_data(source)

    def get_forces(self, source: Dict[str, Any]) -> Dict[str, Any]:
        value = self.get_data(source, path='.varray.v')
        if value is None:
            return {}
        return dict(forces=value, npoints=len(value), rank=[3])


class VASPXMLParser:
    def parse(
        self,
        mainfile: 'str',
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: 'dict[str, EntryArchive]' = None,
    ) -> None:
        logger.info(self.__class__.__name__, parameter=configuration.parameter)

        data_parser = MetainfoParser()
        data_parser.annotation_key = XML_ANNOTATION_KEY

        data = Simulation()
        xml_parser = VasprunParser(filepath=mainfile)

        data_parser.data_object = data
        xml_parser.convert(data_parser)

        data_parser = MetainfoParser()
        data_parser.annotation_key = XML2_ANNOTATION_KEY
        data_parser.data_object = data
        xml_parser.convert(data_parser)

        archive.data = data

        # close file objects
        # data_parser.close()
        # xml_parser.close()
        self.data_parser = data_parser
        self.xml_parser = xml_parser
