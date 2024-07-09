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

import numpy as np
from nomad.config import config
from nomad.metainfo import (
    MEnum,
    Quantity,
    SchemaPackage,
)
from nomad_simulations.schema_packages.properties import TotalEnergy
from nomad_simulations.schema_packages.properties.energies import BaseEnergy

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.schema_packages:mypackage'
)

m_package = SchemaPackage()


# class DoubleCountingCorrection(BaseEnergy):  # no extra class, label via type
#     value = Quantity(
#         type=np.dtype(np.float64),
#         unit='eV',
#     )
#     type  # from physical property (like Chema BandGap direct/indirect label)
#
#     # Needed?
#     def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
#         super().normalize(archive, logger)
#
#         logger.info('MySchema.normalize', parameter=configuration.parameter)
#         self.message = f'Hello {self.name}!'


# class HartreeDCEnergy(DoubleCountingCorrection):
#     value = DoubleCountingCorrection.value


# class XCdcEnergy(DoubleCountingCorrection):
#     value = DoubleCountingCorrection.value


# class Outputs(Outputs):
#     m_def = Section(
#         validate=False,
#         extends_base_section=True,
#     )

#     # add a new section for the custom output
#     hartreedc = SubSection(
#         sub_section=HartreeDCEnergy.m_def,
#         repeats=True,
#     )

#     xcdc = SubSection(
#         sub_section=XCdcEnergy.m_def,
#         repeats=True,
#     )


class DoubleCountingEnergy(BaseEnergy):
    value = Quantity(
        type=np.dtype(np.float64),
        unit='eV',
    )

    type = Quantity(
        type=MEnum('double_counting'),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        if not self.type:
            self.type = 'double_counting'


class HartreeDCEnergy(DoubleCountingEnergy):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class XCdcEnergy(DoubleCountingEnergy):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class RestEnergy(BaseEnergy):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class TotalEnergy(TotalEnergy):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        if self.total_energy:
            for total_energy in self.total_energy:
                if total_energy.value and total_energy.contributions:
                    value = total_energy.value
                    for contribution in total_energy.contributions:
                        value -= contribution.value
                    total_energy.rest_energy.append(RestEnergy(value=value))


m_package.__init_metainfo__()
