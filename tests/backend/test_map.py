from ratroyale.backend.map import Map


def test_map_load_save(example_map: Map) -> None:
    map_bytes = example_map.save()
    assert map_bytes == Map.load(map_bytes).save()
