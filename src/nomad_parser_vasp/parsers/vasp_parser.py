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
from nomad.parsing.file_parser.xml_parser import XMLParser
from nomad.parsing.parser import MatchingParser
from nomad.units import ureg
from nomad_simulations.schema_packages.general import Simulation

configuration = config.get_plugin_entry_point('nomad_parser_vasp.parsers:myparser')

from .schema import (
    HartreeDCEnergy,
    Outputs,
    TotalEnergy,
    XCdcEnergy,
)


class VASPParser(MatchingParser):
    def parser(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        logger.info('VASPParser.parse', parameter=configuration.parameter)
        xml_reader = XMLParser(mainfile=mainfile)  # XPath syntax

        def xml_get(path: str, slicer=slice(0, 1), fallback=None):
            try:
                return xml_reader.parse(path)._results[path][slicer]
            except KeyError:
                return fallback

        # "///separator[@name='electronic exchange-correlation']/i[@name='METAGGA']"
        # <separator name="electronic exchange-correlation" >
        #   <i type="logical" name="LASPH"> F  </i>
        #   <i type="logical" name="LMETAGGA"> F  </i>
        # </separator>

        # "///energy/i[@name='hartreedc']"
        # "///energy/i[@name='XCdc']"
        # <energy>
        #     <i name="alphaZ">    117.79184427 </i>
        #     <i name="ewald">  -1525.97595329 </i>
        #     <i name="hartreedc">   -409.06768234 </i>
        #     <i name="XCdc">    -47.45226295 </i>
        #     <i name="pawpsdc">   1356.25396662 </i>
        #     <i name="pawaedc">  -1245.44542245 </i>
        #     <i name="eentropy">     -0.00003963 </i>
        #     <i name="bandstr">     20.67684976 </i>
        #     <i name="atom">   1849.67745644 </i>
        #     <i name="e_fr_energy">    116.45875643 </i>
        #     <i name="e_wo_entrp">    116.45879606 </i>
        #     <i name="e_0_energy">    116.45876964 </i>
        # </energy>

        total_energy = xml_get("///energy/i[@name='e_fr_energy']")
        hartreedc = xml_get("///energy/i[@name='hartreedc']")
        xcdc = xml_get("///energy/i[@name='XCdc']")

        simulation = Simulation()
        output = Outputs()
        simulation.outputs.append(output)
        output.total_energy.append(TotalEnergy(value=total_energy * ureg.eV))

        output.total_energy[0].contributions.append(
            HartreeDCEnergy(value=hartreedc * ureg.eV)
        )
        output.total_energy[0].contributions.append(XCdcEnergy(value=xcdc * ureg.eV))
