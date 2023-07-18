

def test_get_config_data(results_manager):
    assert results_manager.same_restaurant_votes_weights == [1, 0.5, 0.25]
    assert results_manager.max_allowed_votes == 6


def test_calculate_results(results_manager, multiple_votes):
    # todo: change to expected result and check other way as well
    results = results_manager.calculate_results(multiple_votes)
    assert results
