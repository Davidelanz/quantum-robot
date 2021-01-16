from qrobot.bursts import ZeroBurst


def test_burst():
    burst = ZeroBurst()
    assert burst("0010101010") == 6/10
