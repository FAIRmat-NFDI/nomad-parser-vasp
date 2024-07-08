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
from nomad_simulations.model_system import AtomicCell
from nomad.parsing.file_parser.xml_parser import XMLParser

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:xml_entry_point'
)


class VasprunXMLParser(MatchingParser):
    convert_xc: dict[str, str] = {
        '--': 'GGA_XC_PBE',
        'PE': 'GGA_XC_PBE',
    }

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] = None,
    ) -> None:
        logger.info('VasprunXMLParser.parse', parameter=configuration.parameter)
        xml_reader = XMLParser(mainfile=mainfile)  # XPath syntax

        def xml_get(path: str, index: int = 0):
            try:
                return xml_reader.parse(path)._results[path][index]
            except KeyError:
                return

        archive.data = Simulation(
            program=Program(
                name='VASP',
                version=xml_get("//generator/i[@name='version']"),
            ),
            model_method=[
                DFT(
                    xc_functionals=[
                        XCFunctional(
                            libxc_name=self.convert_xc.get(
                                xml_get(
                                    "///separator[@name='electronic exchange-correlation']/i[@name='LDA']"
                                ),
                                {},
                            )
                            .get(
                                xml_get(
                                    "///separator[@name='electronic exchange-correlation']/i[@name='METAGGA']"
                                ),
                                {},
                            )
                            .get(
                                xml_get(
                                    "///separator[@name='electronic exchange-correlation']/i[@name='GGA']"
                                ),
                                'PE',
                            ),
                        ),
                    ],
                ),
            ],
        )

        if positions := xml_get("structure/varray[@name='positions']/v").any():
            atomic_cell = AtomicCell(
                positions=positions,
            )
            archive.data.model_system.append(atomic_cell)
