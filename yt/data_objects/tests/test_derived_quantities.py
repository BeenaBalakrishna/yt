from __future__ import division

import numpy as np
import yt

from yt.testing import \
    fake_random_ds, \
    fake_sph_orientation_ds, \
    assert_equal, \
    assert_rel_equal, \
    requires_file

def setup():
    from yt.config import ytcfg
    ytcfg["yt","__withintesting"] = "True"

def test_extrema():
    for nprocs in [1, 2, 4, 8]:
        ds = fake_random_ds(16, nprocs = nprocs, fields = ("density",
                "velocity_x", "velocity_y", "velocity_z"))
        for sp in [ds.sphere("c", (0.25, 'unitary')), ds.r[0.5,:,:]]:
            mi, ma = sp.quantities["Extrema"]("density")
            assert_equal(mi, np.nanmin(sp["density"]))
            assert_equal(ma, np.nanmax(sp["density"]))
            dd = ds.all_data()
            mi, ma = dd.quantities["Extrema"]("density")
            assert_equal(mi, np.nanmin(dd["density"]))
            assert_equal(ma, np.nanmax(dd["density"]))
            sp = ds.sphere("max", (0.25, 'unitary'))
            assert_equal(np.any(np.isnan(sp["radial_velocity"])), False)
            mi, ma = dd.quantities["Extrema"]("radial_velocity")
            assert_equal(mi, np.nanmin(dd["radial_velocity"]))
            assert_equal(ma, np.nanmax(dd["radial_velocity"]))

def test_average():
    for nprocs in [1, 2, 4, 8]:
        ds = fake_random_ds(16, nprocs = nprocs, fields = ("density",))
        for ad in [ds.all_data(), ds.r[0.5, :, :]]:

            my_mean = ad.quantities["WeightedAverageQuantity"]("density", "ones")
            assert_rel_equal(my_mean, ad["density"].mean(), 12)

            my_mean = ad.quantities["WeightedAverageQuantity"]("density", "cell_mass")
            a_mean = (ad["density"] * ad["cell_mass"]).sum() / ad["cell_mass"].sum()
            assert_rel_equal(my_mean, a_mean, 12)

def test_variance():
    for nprocs in [1, 2, 4, 8]:
        ds = fake_random_ds(16, nprocs = nprocs, fields = ("density", ))
        for ad in [ds.all_data(), ds.r[0.5, :, :]]:

            my_std, my_mean = ad.quantities["WeightedVariance"]("density", "ones")
            assert_rel_equal(my_mean, ad["density"].mean(), 12)
            assert_rel_equal(my_std, ad["density"].std(), 12)

            my_std, my_mean = ad.quantities["WeightedVariance"]("density", "cell_mass")
            a_mean = (ad["density"] * ad["cell_mass"]).sum() / ad["cell_mass"].sum()
            assert_rel_equal(my_mean, a_mean, 12)
            a_std = np.sqrt((ad["cell_mass"] * (ad["density"] - a_mean)**2).sum() / 
                            ad["cell_mass"].sum())
            assert_rel_equal(my_std, a_std, 12)

def test_max_location():
    for nprocs in [1, 2, 4, 8]:
        ds = fake_random_ds(16, nprocs = nprocs, fields = ("density", ))
        for ad in [ds.all_data(), ds.r[0.5, :, :]]:

            mv, x, y, z = ad.quantities.max_location(("gas", "density"))

            assert_equal(mv, ad["density"].max())

            mi = np.argmax(ad["density"])

            assert_equal(ad["x"][mi], x)
            assert_equal(ad["y"][mi], y)
            assert_equal(ad["z"][mi], z)

def test_min_location():
    for nprocs in [1, 2, 4, 8]:
        ds = fake_random_ds(16, nprocs = nprocs, fields = ("density", ))
        for ad in [ds.all_data(), ds.r[0.5, :, :]]:

            mv, x, y, z = ad.quantities.min_location(("gas", "density"))

            assert_equal(mv, ad["density"].min())

            mi = np.argmin(ad["density"])

            assert_equal(ad["x"][mi], x)
            assert_equal(ad["y"][mi], y)
            assert_equal(ad["z"][mi], z)

def test_sample_at_min_field_values():
    for nprocs in [1, 2, 4, 8]:
        ds = fake_random_ds(16, nprocs = nprocs,
            fields = ("density", "temperature", "velocity_x"))
        for ad in [ds.all_data(), ds.r[0.5, :, :]]:

            mv, temp, vm = ad.quantities.sample_at_min_field_values(
                "density", ["temperature", "velocity_x"])

            assert_equal(mv, ad["density"].min())

            mi = np.argmin(ad["density"])

            assert_equal(ad["temperature"][mi], temp)
            assert_equal(ad["velocity_x"][mi], vm)

def test_sample_at_max_field_values():
    for nprocs in [1, 2, 4, 8]:
        ds = fake_random_ds(16, nprocs = nprocs,
            fields = ("density", "temperature", "velocity_x"))
        for ad in [ds.all_data(), ds.r[0.5, :, :]]:

            mv, temp, vm = ad.quantities.sample_at_max_field_values(
                "density", ["temperature", "velocity_x"])

            assert_equal(mv, ad["density"].max())

            mi = np.argmax(ad["density"])

            assert_equal(ad["temperature"][mi], temp)
            assert_equal(ad["velocity_x"][mi], vm)

def test_in_memory_sph_derived_quantities():
    ds = fake_sph_orientation_ds()
    ad = ds.all_data()

    ang_mom = ad.quantities.angular_momentum_vector()
    assert_equal(ang_mom, [0, 0, 0])

    bv = ad.quantities.bulk_velocity()
    assert_equal(bv, [0, 0, 0])

    com = ad.quantities.center_of_mass()
    assert_equal(com, [1/7, (1+2)/7, (1+2+3)/7])

    ex = ad.quantities.extrema(['x', 'y', 'z'])
    for fex, ans in zip(ex, [[0, 1], [0, 2], [0, 3]]):
        assert_equal(fex, ans)

    for d, v, l in zip('xyz', [1, 2, 3], [[1, 0, 0], [0, 2, 0], [0, 0, 3]]):
        max_d, x, y, z = ad.quantities.max_location(d)
        assert_equal(max_d, v)
        assert_equal([x, y, z], l)

    for d in 'xyz':
        min_d, x, y, z = ad.quantities.min_location(d)
        assert_equal(min_d, 0)
        assert_equal([x, y, z], [0, 0, 0])

    tot_m = ad.quantities.total_mass()
    assert_equal(tot_m, [7, 0])

    weighted_av_z = ad.quantities.weighted_average_quantity('z', 'z')
    assert_equal(weighted_av_z, 7/3)

iso_collapse = "IsothermalCollapse/snap_505"
tipsy_gal = 'TipsyGalaxy/galaxy.00300'

@requires_file(iso_collapse)
@requires_file(tipsy_gal)
def test_sph_datasets_derived_quantities():
    for fname in [tipsy_gal, iso_collapse]:
        ds = yt.load(fname)
        ad = ds.all_data()
        ad.quantities.angular_momentum_vector()
        ad.quantities.bulk_velocity(True, True)
        ad.quantities.center_of_mass(True, True)
        ad.quantities.extrema(['density', 'temperature'])
        ad.quantities.min_location('density')
        ad.quantities.max_location('density')
        ad.quantities.total_mass()
        ad.quantities.weighted_average_quantity('density', 'mass')
