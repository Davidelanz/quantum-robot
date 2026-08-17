from qrobot.bursts import OneBurst


def test_burst():
    burst = OneBurst()
    assert burst("0000") == 0.0
    assert burst("0010101010") == 4 / 10
    assert burst("1111") == 1.0
