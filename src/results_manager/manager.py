import json
from collections import defaultdict

from results_manager import consts
from schemas.vote import Vote


class TooManyVotesError(Exception):
    pass


def _tie_break(votes: list[Vote], candidates: list[str]) -> int:
    candidate_to_voter_ids = defaultdict(list)
    for vote in votes:
        if vote.restaurant_id in candidates:
            candidate_to_voter_ids[vote.restaurant_id].append(vote.voter_id)
    candidate_to_num_of_distinct_voters = {item[0]: len(set(item[1])) for item in candidate_to_voter_ids.items()}
    if candidate_to_num_of_distinct_voters[candidates[0]] > candidate_to_num_of_distinct_voters[candidates[1]]:
        return candidates[0]
    # There's still a chance for tie, arbitrary will be the second
    return candidates[1]


class ResultsManager:
    def __init__(self):
        self._json_path = "./results_manager/results_manager_config.json"
        config_data = json.load(open(self._json_path, "r"))
        self.max_allowed_votes = config_data[consts.MAX_ALLOWED_VOTES]
        self.same_restaurant_votes_weights = config_data[consts.SAME_RESTAURANT_VOTES_WEIGHTS]

    @staticmethod
    def calculate_results(votes: list[Vote]) -> dict[int, int]:
        restaurant_score_by_restaurant_ids = defaultdict(int)
        for vote in votes:
            restaurant_id = vote.restaurant_id
            if not restaurant_id:
                # handling count of protest votes
                # todo: maybe  i'll just remove the protest vote, it'll make things easier
                restaurant_id = "protest vote"
            restaurant_score_by_restaurant_ids[restaurant_id] += vote.vote_score
        return restaurant_score_by_restaurant_ids

    def get_winner(self, votes: list[Vote]):
        restaurant_score_by_restaurant_ids = self.calculate_results(votes)
        sorted_scores = sorted(restaurant_score_by_restaurant_ids.items(), key=lambda tup: tup[1], reverse=True)
        # todo: handle empty list
        if len(sorted_scores) == 1 or sorted_scores[0][1] > sorted_scores[1][1]:
            # Validation for tie
            return sorted_scores[0][0]
        return _tie_break(votes, candidates=[sorted_scores[0][0], sorted_scores[1][0]])

    def calculate_vote_score(self, vote, previous_votes):
        relevant_votes = []
        for v in previous_votes:
            if v.voter_id == vote.voter_id and int(v.restaurant_id) == int(vote.restaurant_id):
                relevant_votes.append(v)
        return self.get_vote_score(len(relevant_votes))

    def get_vote_score(self, vote_index):
        if vote_index >= len(self.same_restaurant_votes_weights):
            return self.same_restaurant_votes_weights[-1]
        return self.same_restaurant_votes_weights[vote_index]
