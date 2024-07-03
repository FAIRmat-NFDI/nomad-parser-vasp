from nomad.datamodel.datamodel import (
    EntryArchive,
)
from structlog.stdlib import (
    BoundLogger,
)

from nomad.config import config
from nomad.parsing import MatchingParser
from nomad.parsing.file_parser.mapping_parser import (
    MappingAnnotationModel,
    MetainfoParser,
    XMLParser,
)
from nomad_simulations.schema_packages.general import Simulation, Program
from nomad_simulations.schema_packages.model_system import (
    ModelSystem,
    AtomicCell,
)
from nomad_simulations.schema_packages.model_method import (
    DFT,
    XCFunctional,
)
from nomad_simulations.schema_packages.outputs import ElectronicEigenvalues
from nomad_simulations.schema_packages.numerical_settings import KMesh

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:xml_entry_point'
)

# TODO move to schema parser and prepare all relevant annotations for every file format


# ! vasprun.xml has many meta fields, explaining field semantics
Simulation.m_def.m_annotations['xml'] = MappingAnnotationModel(path='modeling')

Simulation.program.m_annotations['xml'] = MappingAnnotationModel(path='.generator')


Program.name.m_annotations['xml'] = MappingAnnotationModel(
    path='.i[?"@name"="program"]'
)


Program.version.m_annotations['xml'] = MappingAnnotationModel(
    path='.i[?"@name"="version"]'
)

# ? compilation mode
Program.compilation_host.m_annotations['xml'] = MappingAnnotationModel(
    path='.i[?"@name"="platform"]'
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
