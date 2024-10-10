import os
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
from nomad.parsing.parser import MatchingParser
from nomad_simulations.schema_packages.general import Program, Simulation
from nomad_simulations.schema_packages.model_method import DFT
from nomad_simulations.schema_packages.model_system import ModelSystem
from nomad_simulations.schema_packages.outputs import Outputs
from nomad_simulations.schema_packages.workflow import SinglePoint

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:parser_entry_point'
)


class VASPParser(MatchingParser):
    def parse(
        self, filepath: str, archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> None:
        self.mainfile = filepath
        self.maindir = os.path.dirname(self.mainfile)
        self.basename = os.path.basename(self.mainfile)
        self.archive = archive

        # Adding Simulation to data
        simulation = Simulation()
        simulation.program = Program(name='VASP')
        archive.data = simulation

        # ModelSystem
        model_system = ModelSystem()
        simulation.model_system.append(model_system)

        # ModelMethod
        dft = DFT()
        simulation.model_method.append(dft)

        # Outputs
        outputs = Outputs()
        simulation.outputs.append(outputs)

        # Workflow section
        workflow = SinglePoint()
        # workflow.normalize(archive=archive, logger=logger)
        archive.workflow2 = workflow
