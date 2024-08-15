import numpy as np
from nomad.config import config
from nomad.datamodel.datamodel import EntryArchive
from nomad.parsing import MatchingParser
from nomad.parsing.file_parser.xml_parser import XMLParser
from nomad.units import ureg
from nomad_simulations.schema_packages.general import Program, Simulation
from nomad_simulations.schema_packages.model_method import DFT, XCFunctional
from nomad_simulations.schema_packages.model_system import AtomicCell, ModelSystem
from nomad_simulations.schema_packages.outputs import Outputs
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

        ####################################################
        # Parse the basic program, method, and system data #
        ####################################################
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

        #####################################################
        # Get the energy data from the raw simulation files #
        #####################################################
        total_energy = xml_get("i[@name='e_fr_energy']", slice(-2, -1))
        total_energy = total_energy[0] * ureg.eV if total_energy else None
        hartreedc = xml_get("i[@name='hartreedc']", slice(-2, -1))
        hartreedc = hartreedc[0] * ureg.eV if hartreedc else None
        xcdc = xml_get("i[@name='XCdc']", slice(-2, -1))
        xcdc = xcdc[0] * ureg.eV if xcdc else None

        ####################################################
        # Create the outputs section, populate it with the #
        # parsed energies, and add it to the archive       #
        ####################################################
        output = Outputs()
        archive.data.outputs.append(output)
        output.total_energy.append(TotalEnergy(value=total_energy))
        output.total_energy[0].contributions.append(HartreeDCEnergy(value=hartreedc))
        output.total_energy[0].contributions.append(XCdcEnergy(value=xcdc))

        ##############################################################
        # Add a new contribution to the total energy that quantifies #
        # its unknown contributions (3 ways, choose 1)               #
        ##############################################################

        # Case 1: Don't include UnknownEnergy in parsing
        # Expected Results: UnknownEnergy is added to contribution list by the normalizer

        # # Case 2: Add UnknownEnergy to contribution list in the parser but without a value
        # from nomad_parser_vasp.schema_packages.vasp_schema import UnknownEnergy

        # output.total_energy[0].contributions.append(UnknownEnergy(value=None))
        # # Expected Results: UnknownEnergy value is calculated by the normalizer and placed into this section

        # Case 3: Add UnknownEnergy to contribution list in the parser with a value
        # from nomad_parser_vasp.schema_packages.vasp_schema import UnknownEnergy

        # output.total_energy[0].contributions.append(
        #     UnknownEnergy(value=(total_energy - 2 * hartreedc - xcdc))
        # )
        # Expected Results: normalizer does not change the value of UnknownEnergy
        # (for testing purposes we subtract double the hartreedc value)
