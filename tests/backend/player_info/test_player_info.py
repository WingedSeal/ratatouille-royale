from ratroyale.backend.player_info.player_info import PlayerInfo


def test_player_info_test_load(example_player_info: PlayerInfo) -> None:
    player_info_bytes = example_player_info.save()
    assert player_info_bytes == PlayerInfo.load(player_info_bytes).save()
