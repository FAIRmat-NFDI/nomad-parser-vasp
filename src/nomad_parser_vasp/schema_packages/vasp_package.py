from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from nomad.metainfo import SchemaPackage
from nomad.parsing.file_parser.mapping_parser import MappingAnnotationModel
from nomad_simulations.schema_packages import (
    general,
    model_method,
    model_system,
    numerical_settings,
    outputs,
    properties,
)

m_package = SchemaPackage()

OUTCAR_ANNOTATION_KEY = 'outcar'
XML_ANNOTATION_KEY = 'xml'
XML2_ANNOTATION_KEY = 'xml2'


class Program(general.Program):
    general.Program.name.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
        mapper='.i[?"@name"==\'program\'] | [0].__value',
    )

    general.Program.version.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
        mapper='.i[?"@name"==\'version\'] | [0].__value',
    )

    general.Program.version.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=('get_version', ['.@']),
        )
    )

    # Apply similar logic here
    general.Program.compilation_host.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.i[?"@name"==\'platform\'] | [0].__value')
    )


class XCFunctional(model_method.XCFunctional):
    model_method.XCFunctional.libxc_name.m_annotations = dict(
        xml=MappingAnnotationModel(
            mapper='.i[?"@name"==\'GGA\'] | [0].__value'  # TODO add LDA & mGGA, convert_xc
        )
    )


class KMesh(numerical_settings.KMesh):
    numerical_settings.KMesh.grid.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper='.generation.v[?"@name"==\'divisions\'] | [0].__value'
        )
    )

    numerical_settings.KMesh.offset.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper='.generation.v[?"@name"==\'shift\'] | [0].__value'
        )
    )

    numerical_settings.KMesh.points.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.varray[?"@name"==\'kpointlist\'].v | [0]')
    )

    numerical_settings.KMesh.weights.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.varray[?"@name"==\'weights\'].v | [0]')
    )


class KSpace(numerical_settings.KSpace):
    numerical_settings.KSpace.k_mesh.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.@')
    )


class DFT(model_method.DFT):
    model_method.DFT.xc_functionals.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper='.separator[?"@name"==\'electronic exchange-correlation\']'
        )
    )

    model_method.DFT.exact_exchange_mixing_factor.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=(
                'mix_alpha',
                [
                    '.i[?"@name"==\'HFALPHA\'] | [0].__value',
                    '.i[?"@name"==\'LHFCALC\'] | [0].__value',
                ],
            )
        )
    )  # TODO convert vasp bool

    numerical_settings.KSpace.m_def.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='modeling.kpoints')
    )


class AtomicCell(model_system.AtomicCell):
    model_system.AtomicCell.positions.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.varray.v', unit='angstrom')
    )
    model_system.AtomicCell.positions.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper='.positions_forces', unit='angstrom', search='@ | [0]'
        )
    )

    model_system.AtomicCell.lattice_vectors.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper='.crystal.varray[?"@name"==\'basis\'] | [0].v', unit='angstrom'
        )
    )
    model_system.AtomicCell.lattice_vectors.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper='.lattice_vectors', unit='angstrom', search='@ | [0]'
        )
    )


class ModelSystem(general.ModelSystem):
    model_system.AtomicCell.m_def.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.structure')
    )
    model_system.AtomicCell.m_def.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.@')
    )


class EnergyContribution(properties.energies.EnergyContribution):
    properties.energies.EnergyContribution.name.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='."@name"')
    )
    properties.energies.EnergyContribution.name.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.name')
    )
    # value is already defined in TotalEnergy since they use the same def
    # get_energy function should be able to handle extraction from both sources


class TotalEnergy(properties.energies.TotalEnergy):
    properties.energies.TotalEnergy.value.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=(
                'get_data',
                ['.@'],
                dict(path='.i[?"@name"==\'e_fr_energy\'] | [0].__value'),
            ),
            unit='eV',
        )
    )
    properties.energies.TotalEnergy.value.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=('get_data', ['.@'], dict(path='.energy_total')), unit='eV'
        )
    )

    properties.energies.TotalEnergy.contributions.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=('get_energy_contributions', ['.i'], dict(exclude=['e_fr_energy']))
        )
    )
    properties.energies.TotalEnergy.contributions.m_annotations[
        OUTCAR_ANNOTATION_KEY
    ] = MappingAnnotationModel(
        mapper=('get_energy_contributions', ['.@'], dict(exclude=['energy_total']))
    )


class TotalForce(properties.forces.TotalForce):
    properties.forces.TotalForce.value.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=('get_data', ['.@'], dict(path='.varray.v')), unit='eV/angstrom'
        )
    )
    properties.forces.TotalForce.value.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=('get_data', ['.@'], dict(path='.positions_forces | [1]')),
            unit='eV/angstrom',
        )
    )


class ElectronicEigenvalues(outputs.ElectronicEigenvalues):
    outputs.ElectronicEigenvalues.n_bands.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='length(.array.set.set.set[0].r)')
    )
    outputs.ElectronicEigenvalues.n_bands.m_annotations[XML2_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='length(.array.set.set.set[0].r)')
    )
    outputs.ElectronicEigenvalues.n_bands.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.n_bands')
    )

    # TODO This only works for non-spin pol
    outputs.ElectronicEigenvalues.occupation.m_annotations[XML2_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper=('get_eigenvalues', ['.array.set.set.set[].r']))
    )
    outputs.ElectronicEigenvalues.occupation.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.occupations')
    )
    outputs.ElectronicEigenvalues.value.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.eigenvalues')
    )


class Ouputs(outputs.Outputs):
    outputs.Outputs.total_energies.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.energy')
    )
    outputs.Outputs.total_energies.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.energies')
    )
    outputs.Outputs.total_forces.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.@')
    )
    outputs.Outputs.total_forces.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.@')
    )
    outputs.Outputs.electronic_eigenvalues.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.eigenvalues')
    )
    outputs.Outputs.electronic_eigenvalues.m_annotations[XML2_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.eigenvalues')
    )
    outputs.Outputs.electronic_eigenvalues.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(
            mapper=('get_eigenvalues', ['.eigenvalues', 'parameters'])
        )
    )


class Simulation(general.Simulation):
    general.Simulation.program.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.generator')
    )
    general.Simulation.program.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.header')
    )

    model_method.DFT.m_def.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
        mapper='.parameters.separator[?"@name"==\'electronic\']'
    )

    general.Simulation.model_system.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.calculation')
    )
    general.Simulation.model_system.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.calculation')
    )

    general.Simulation.outputs.m_annotations[XML_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.calculation')
    )
    general.Simulation.outputs.m_annotations[XML2_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.calculation')
    )
    general.Simulation.outputs.m_annotations[OUTCAR_ANNOTATION_KEY] = (
        MappingAnnotationModel(mapper='.calculation')
    )


# note: vasprun.xml has many meta fields, explaining field semantics
Simulation.m_def.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='modeling'
)
Simulation.m_def.m_annotations[XML2_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='modeling'
)
Simulation.m_def.m_annotations[OUTCAR_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='@'
)


"""

# ? target <structure name="initialpos" > and <structure name="finalpos" >

"""

"""
...forces.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='varray[?"@name"==\'forces\'] | [0].__value'
)

...stress.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='varray[?"@name"==\'stress\'] | [0].__value'
)

cell_volume.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='crystal.i[?"@name"==\'volume\'] | [0].__value'
)

reciprocal_lattice_vectors.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='crystal.varray[?"@name"==\'rec_basis\'] | [0].__value'
)

total_free_energy.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='calculation.energy.i[?"@name"==\'e_fr_energy\'] | [0].__value'
)

total_internal_energy.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='calculation.energy.i[?"@name"==\'e_0_energy\'] | [0].__value'
)

...eigenvalues.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='.eigenvalues.array'
)

ElectronicEigenvalues.spin_channel.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper='.eigenvalues.set.set[?comment==\'spin 1\'] | [0].__value'
)

ElectronicEigenvalues.reciprocal_cell.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper=ElectronicEigenvalues.spin_channel.m_annotations[XML_ANNOTATION_KEY]
    + '.set[?comment==\'kpoint 1\'] | [0].__value'
)

ElectronicEigenvalues.occupation.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper=ElectronicEigenvalues.reciprocal_cell.m_annotations[XML_ANNOTATION_KEY] + '.r[0] | [0].__value'
)

ElectronicEigenvalues.value.m_annotations[XML_ANNOTATION_KEY] = MappingAnnotationModel(
    mapper=ElectronicEigenvalues.reciprocal_cell.m_annotations[XML_ANNOTATION_KEY] + '.r[1] | [0].__value'
)
"""

m_package.__init_metainfo__()
