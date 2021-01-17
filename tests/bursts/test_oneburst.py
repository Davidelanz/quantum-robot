from qrobot.bursts import OneBurst


def test_burst():
    burst = OneBurst()
    assert burst("0010101010") == 4/10
