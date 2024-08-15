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
    def __init__(
        self, m_def: 'Section' = None, m_context: 'Context' = None, **kwargs
    ) -> None:
        super().__init__(m_def, m_context, **kwargs)
        self.name = self.m_def.name

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class XCdcEnergy(DoubleCountingEnergy):
    def __init__(
        self, m_def: 'Section' = None, m_context: 'Context' = None, **kwargs
    ) -> None:
        super().__init__(m_def, m_context, **kwargs)
        self.name = self.m_def.name

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class UnknownEnergy(EnergyContribution):
    def __init__(
        self, m_def: 'Section' = None, m_context: 'Context' = None, **kwargs
    ) -> None:
        super().__init__(m_def, m_context, **kwargs)
        self.name = self.m_def.name

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
        unknown_exists = False
        unknown_has_value = False
        i_unknown = None
        for i_cont, contribution in enumerate(self.contributions):
            if contribution.name == 'UnknownEnergy':
                unknown_exists = True
                i_unknown = i_cont
                unknown_has_value = True if contribution.value else False

            if not contribution.value:
                continue

            value -= contribution.value

        if unknown_exists:
            if not unknown_has_value:
                self.contributions[i_unknown].value = value
        else:
            self.contributions.append(UnknownEnergy(value=value))
            self.contributions[-1].normalize(archive, logger)
