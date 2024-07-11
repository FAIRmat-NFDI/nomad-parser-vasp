import nomad_simulations
from nomad.metainfo import MEnum, Quantity
from nomad_simulations.schema_packages.properties.energies import EnergyContribution


class DoubleCountingEnergy(EnergyContribution):
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


class UnknownEnergy(EnergyContribution):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class TotalEnergy(nomad_simulations.schema_packages.properties.TotalEnergy):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        if not self.value:
            return
        if not self.contributions:
            return

        value = self.value
        unknown_energy_exists = False
        for contribution in self.contributions:
            if not contribution.value:
                continue
            if contribution.name == 'UnknownEnergy':
                unknown_energy_exists = True

            value -= contribution.value
        if not unknown_energy_exists:
            self.contributions.append(UnknownEnergy(value=value))
