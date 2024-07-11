import numpy as np
from nomad.config import config
from nomad.datamodel.datamodel import EntryArchive
from nomad.parsing import MatchingParser
from nomad.parsing.file_parser.xml_parser import XMLParser
from nomad_simulations.general import Program, Simulation
from nomad_simulations.model_method import DFT, XCFunctional
from nomad_simulations.model_system import AtomicCell, ModelSystem
from nomad_simulations.outputs import Outputs
from structlog.stdlib import BoundLogger

from nomad_parser_vasp.schema_packages.vasp_schema import (
    HartreeDCEnergy,
    TotalEnergy,
    XCdcEnergy,
)

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

        def xml_get(path: str, slicer=slice(0, 1), fallback=None):
            try:
                return xml_reader.parse(path)._results[path][slicer]
            except KeyError:
                return fallback

        archive.data = Simulation(
            program=Program(
                name='VASP',
                version=xml_get("//generator/i[@name='version']")[0],
            ),
            model_method=[
                DFT(
                    xc_functionals=[
                        XCFunctional(
                            libxc_name=self.convert_xc.get(
                                xml_get(
                                    "///separator[@name='electronic exchange-correlation']/i[@name='LSDA']"
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

        if (
            positions := xml_get(
                "structure[@name='finalpos']/./varray[@name='positions']/v",
                slice(None),
                fallback=np.array([]),
            )
        ).any():
            archive.data.model_system.append(
                ModelSystem(cell=[AtomicCell(positions=positions)])
            )

        total_energy = xml_get("i[@name='e_fr_energy']", slice(-2, -1))
        hartreedc = xml_get("i[@name='hartreedc']", slice(-2, -1))
        xcdc = xml_get("i[@name='XCdc']", slice(-2, -1))

        output = Outputs()
        archive.simulation.outputs.append(output)
        output.total_energy.append(TotalEnergy(value=total_energy * ureg.eV))

        output.total_energy[0].contributions.append(
            HartreeDCEnergy(value=hartreedc * ureg.eV)
        )
        output.total_energy[0].contributions.append(XCdcEnergy(value=xcdc * ureg.eV))
