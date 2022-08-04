import geopandas

def setup_geopandas():
    countries_mapping = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    countries_mapping = lowres_fix(countries_mapping)
    countries_mapping = countries_mapping[(countries_mapping.name != "Antarctica") &
                                          (countries_mapping.iso_a3 != "-99")]
    return countries_mapping

def lowres_fix(world):
    """There is an issue with the map data source from geopandas where
    ISO codes are missing for several countries. This fix was proposed
    by @tommycarstensen at
    https://github.com/geopandas/geopandas/issues/1041

    :param world: dataframe (read in with geopandas)
    :return: dataframe (geopandas formatted)
    """
    world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
    world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
    world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
    world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'RKS'
    return world

