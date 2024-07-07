from nomad.datamodel.datamodel import (
    EntryArchive,
)
from structlog.stdlib import (
    BoundLogger,
)

from nomad.config import config
from nomad.parsing import MatchingParser
from nomad_simulations.general import Simulation, Program
from nomad_simulations.model_method import DFT, XCFunctional
from nomad_simulations.model_system import ModelSystem, AtomicCell
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
        xml_reader = XMLParser(mainfile=mainfile)  # XPath syntax

        def xml_get(path: str):
            return xml_reader.parse(path)._results[path]

        archive.data = Simulation(
            program=Program(
                name='VASP',
                version=xml_get("//generator/i[@name='version']")[0],
            ),
            model_method=DFT(
                xc_functional=XCFunctional(
                    name=xml_get("i[@name='GGA']")[0],
                ),
            ),
            model_system=AtomicCell(
                cell=AtomicCell(
                    positions=xml_get("structure/varray[@name='positions']/v")[0],
                ),
            ),
        )
