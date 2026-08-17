from qrobot.bursts import ZeroBurst


def test_burst():
    burst = ZeroBurst()
    assert burst("0000") == 1.0
    assert burst("0010101010") == 6 / 10
    assert burst("1111") == 0.0
