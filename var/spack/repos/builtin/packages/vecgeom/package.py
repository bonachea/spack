# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack import *


class Vecgeom(CMakePackage, CudaPackage):
    """The vectorized geometry library for particle-detector simulation
    (toolkits)."""

    homepage = "https://gitlab.cern.ch/VecGeom/VecGeom"
    url = "https://gitlab.cern.ch/VecGeom/VecGeom/-/archive/v1.1.6/VecGeom-v1.1.6.tar.gz"
    git = "https://gitlab.cern.ch/VecGeom/VecGeom.git"

    maintainers = ['drbenmorgan', 'sethrj']

    version('master', branch='master')
    version('1.1.6', sha256='c4806a6b67d01b40074b8cc6865d78574a6a1c573be51696f2ecdf98b9cb954a')
    version('1.1.5', sha256='da674f3bbc75c30f56c1a2d251fa8930c899f27fa64b03a36569924030d87b95')
    version('1.1.3', sha256='ada09e8b6b2fa6c058290302b2cb5a6c2e644192aab1623c31d18c6a2f4c01c8')
    version('1.0.1', sha256='1eae7ac9014c608e8d8db5568058b8c0fea1a1dc7a8f54157a3a1c997b6fd9eb')
    version('0.5.2', tag='v00.05.02',
            commit='a7e0828c915ff936a79e672d1dd84b087a323b51')
    version('0.3.rc', sha256='a87a9ea4ab126b59ff9c79182bc0911ead3d76dd197194742e2a35ccd341299d')

    _cxxstd_values = ('11', '14', '17')
    variant('cxxstd', default='11', values=_cxxstd_values, multi=False,
            description='Use the specified C++ standard when building')
    variant('gdml', default=True,
            description='Support native GDML geometry descriptions')
    variant('geant4', default=False,
            description='Support Geant4 geometry construction')
    variant('root', default=False,
            description='Support ROOT geometry construction')
    variant('shared', default=True,
            description='Build shared libraries')

    depends_on('veccore@0.5.2:', type=('build', 'link'), when='@1.1.0:')
    depends_on('veccore@0.4.2', type=('build', 'link'), when='@:1.0')
    depends_on('veccore+cuda', type=('build', 'link'), when='+cuda')

    conflicts('+cuda', when='@:1.1.5')

    for std in _cxxstd_values:
        depends_on('geant4 cxxstd=' + std, when='+geant4 cxxstd=' + std)
        depends_on('root cxxstd=' + std, when='+root cxxstd=' + std)
        depends_on('veccore cxxstd=' + std, when='cxxstd=' + std)
        depends_on('xerces-c cxxstd=' + std, when='+gdml cxxstd=' + std)

    def cmake_args(self):
        # Possible target options are from the main CMakeLists.txt, assuming
        # "best" is last
        target = self.spec.target
        vecgeom_arch = "sse2 sse3 ssse3 sse4.1 sse4.2 avx avx2".split()
        for feature in reversed(vecgeom_arch):
            if feature.replace('.', '_') in target:
                target_instructions = feature
                break
        else:
            # No features available (could be 'generic' arch)
            target_instructions = 'empty'

        define = CMakePackage.define
        options = [
            define('BACKEND', 'Scalar'),
            define('BUILTIN_VECCORE', False),
            define('NO_SPECIALIZATION', True),
            define('VECGEOM_VECTOR', target_instructions),
            self.define_from_variant('BUILD_SHARED_LIBS', 'shared'),
            self.define_from_variant('CMAKE_CXX_STANDARD', 'cxxstd'),
            self.define_from_variant('CUDA'),
            self.define_from_variant('GDML'),
            self.define_from_variant('GEANT4'),
            self.define_from_variant('ROOT'),
        ]

        # Set testing flags
        build_tests = self.run_tests
        options.extend([
            define('BUILD_TESTING', build_tests),
            define('CTEST', build_tests),
            define('GDMLTESTING', build_tests and '+gdml' in self.spec),
        ])

        if '+cuda' in self.spec:
            arch = self.spec.variants['cuda_arch'].value
            if len(arch) != 1 or arch[0] == 'none':
                raise InstallError("Exactly one cuda_arch must be specified")
            options.append(define('CUDA_ARCH', arch[0]))

        if self.spec.satisfies("@:0.5.2"):
            options.extend([
                define('USOLIDS', True),
                define('USOLIDS_VECGEOM', True),
            ])

        return options
