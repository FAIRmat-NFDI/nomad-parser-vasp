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
)

m_package = SchemaPackage()


class Program(general.Program):
    general.Program.name.m_annotations['xml'] = MappingAnnotationModel(
        path='.i[?"@name"==\'program\'] | [0].__value',
    )

    general.Program.version.m_annotations['xml'] = MappingAnnotationModel(
        path='.i[?"@name"==\'version\'] | [0].__value',
    )

    # Apply similar logic here
    general.Program.compilation_host.m_annotations['xml'] = MappingAnnotationModel(
        path='.i[?"@name"==\'platform\'] | [0].__value'
    )


class XCFunctional(model_method.XCFunctional):
    model_method.XCFunctional.libxc_name.m_annotations = dict(
        xml=MappingAnnotationModel(
            path='.i[?"@name"==\'GGA\'] | [0].__value'  # TODO add LDA & mGGA, convert_xc
        )
    )


class KMesh(numerical_settings.KMesh):
    numerical_settings.KMesh.grid.m_annotations['xml'] = MappingAnnotationModel(
        path='.generation.v[?"@name"==\'divisions\'] | [0].__value'
    )

    numerical_settings.KMesh.offset.m_annotations['xml'] = MappingAnnotationModel(
        path='.generation.v[?"@name"==\'shift\'] | [0].__value'
    )

    numerical_settings.KMesh.points.m_annotations['xml'] = MappingAnnotationModel(
        path='.varray[?"@name"==\'kpointlist\'].v | [0]'
    )

    numerical_settings.KMesh.weights.m_annotations['xml'] = MappingAnnotationModel(
        path='.varray[?"@name"==\'weights\'].v | [0]'
    )


class KSpace(numerical_settings.KSpace):
    numerical_settings.KSpace.k_mesh.m_annotations['xml'] = MappingAnnotationModel(
        path='.@'
    )


class DFT(model_method.DFT):
    model_method.DFT.xc_functionals.m_annotations['xml'] = MappingAnnotationModel(
        path='.separator[?"@name"==\'electronic exchange-correlation\']'
    )

    model_method.DFT.exact_exchange_mixing_factor.m_annotations['xml'] = (
        MappingAnnotationModel(
            operator=(
                'mix_alpha',
                [
                    '.i[?"@name"==\'HFALPHA\'] | [0].__value',
                    '.i[?"@name"==\'LHFCALC\'] | [0].__value',
                ],
            )
        )
    )  # TODO convert vasp bool

    numerical_settings.KSpace.m_def.m_annotations['xml'] = MappingAnnotationModel(
        path='modeling.kpoints'
    )


class AtomicCell(model_system.AtomicCell):
    model_system.AtomicCell.positions.m_annotations = dict(
        xml=MappingAnnotationModel(path='.varray.v', unit='angstrom')
    )

    model_system.AtomicCell.lattice_vectors.m_annotations['xml'] = (
        MappingAnnotationModel(
            path='.crystal.varray[?"@name"==\'basis\'] | [0].v', unit='angstrom'
        )
    )


class ModelSystem(general.ModelSystem):
    model_system.AtomicCell.m_def.m_annotations['xml'] = MappingAnnotationModel(
        path='.structure'
    )


class TotalEnergy(outputs.TotalEnergy):
    outputs.TotalEnergy.value.m_annotations['xml'] = MappingAnnotationModel(
        path='.energy.i[?"@name"==\'e_fr_energy\'] | [0].__value', unit='eV'
    )


class ElectronicEigenvalues(outputs.ElectronicEigenvalues):
    outputs.ElectronicEigenvalues.n_bands.m_annotations['xml'] = MappingAnnotationModel(
        path='length(.array.set.set.set[0].r)'
    )
    outputs.ElectronicEigenvalues.n_bands.m_annotations['xml2'] = (
        MappingAnnotationModel(path='length(.array.set.set.set[0].r)')
    )
    # TODO This only works for non-spin pol
    outputs.ElectronicEigenvalues.occupation.m_annotations['xml2'] = (
        MappingAnnotationModel(operator=('get_eigenvalues', ['.array.set.set.set[].r']))
    )


class Ouputs(outputs.Outputs):
    outputs.Outputs.total_energies.m_annotations['xml'] = MappingAnnotationModel(
        path='.@'
    )
    outputs.Outputs.electronic_eigenvalues.m_annotations = dict(
        xml=MappingAnnotationModel(path='.eigenvalues'),
        xml2=MappingAnnotationModel(path='.eigenvalues'),
    )


class Simulation(general.Simulation):
    general.Simulation.program.m_annotations['xml'] = MappingAnnotationModel(
        path='.generator'
    )

    model_method.DFT.m_def.m_annotations['xml'] = MappingAnnotationModel(
        path='.parameters.separator[?"@name"==\'electronic\']'
    )

    general.Simulation.model_system.m_annotations['xml'] = MappingAnnotationModel(
        path='.calculation'
    )

    general.Simulation.outputs.m_annotations = dict(
        xml=MappingAnnotationModel(path='.calculation'),
        xml2=MappingAnnotationModel(path='.calculation'),
    )


# note: vasprun.xml has many meta fields, explaining field semantics
Simulation.m_def.m_annotations['xml'] = MappingAnnotationModel(path='modeling')
Simulation.m_def.m_annotations['xml2'] = MappingAnnotationModel(path='modeling')


"""

# ? target <structure name="initialpos" > and <structure name="finalpos" >

"""

"""
...forces.m_annotations['xml'] = MappingAnnotationModel(
    path='varray[?"@name"==\'forces\'] | [0].__value'
)

...stress.m_annotations['xml'] = MappingAnnotationModel(
    path='varray[?"@name"==\'stress\'] | [0].__value'
)

cell_volume.m_annotations['xml'] = MappingAnnotationModel(
    path='crystal.i[?"@name"==\'volume\'] | [0].__value'
)

reciprocal_lattice_vectors.m_annotations['xml'] = MappingAnnotationModel(
    path='crystal.varray[?"@name"==\'rec_basis\'] | [0].__value'
)

total_free_energy.m_annotations['xml'] = MappingAnnotationModel(
    path='calculation.energy.i[?"@name"==\'e_fr_energy\'] | [0].__value'
)

total_internal_energy.m_annotations['xml'] = MappingAnnotationModel(
    path='calculation.energy.i[?"@name"==\'e_0_energy\'] | [0].__value'
)

...eigenvalues.m_annotations['xml'] = MappingAnnotationModel(
    path='.eigenvalues.array'
)

ElectronicEigenvalues.spin_channel.m_annotations['xml'] = MappingAnnotationModel(
    path='.eigenvalues.set.set[?comment==\'spin 1\'] | [0].__value'
)

ElectronicEigenvalues.reciprocal_cell.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.spin_channel.m_annotations['xml']
    + '.set[?comment==\'kpoint 1\'] | [0].__value'
)

ElectronicEigenvalues.occupation.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.reciprocal_cell.m_annotations['xml'] + '.r[0] | [0].__value'
)

ElectronicEigenvalues.value.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.reciprocal_cell.m_annotations['xml'] + '.r[1] | [0].__value'
)
"""

m_package.__init_metainfo__()
