"""Exploration schedule for Reinforcement Learning training."""

class EpsilonDecay:
    def __init__(
        self,
        start_epsilon: float = 1.0,
        min_epsilon: float = 0.05,
        total_episodes: int = 30,
        decay_type: str = "linear",
    ):
        self.start_epsilon = start_epsilon
        self.min_epsilon = min_epsilon
        self.total_episodes = max(1, total_episodes)
        self.decay_type = decay_type

    def get_epsilon(self, episode_idx: int) -> float:
        """Returns the epsilon value for the given episode index (0-indexed)."""
        if episode_idx >= self.total_episodes:
            return self.min_epsilon

        progress = episode_idx / float(self.total_episodes)

        if self.decay_type == "linear":
            eps = self.start_epsilon - progress * (self.start_epsilon - self.min_epsilon)
        elif self.decay_type == "exponential":
            # decays to min_epsilon by total_episodes
            decay_rate = (self.min_epsilon / self.start_epsilon) ** (1.0 / self.total_episodes)
            eps = self.start_epsilon * (decay_rate ** episode_idx)
        else:
            eps = self.start_epsilon - progress * (self.start_epsilon - self.min_epsilon)

        return max(self.min_epsilon, min(self.start_epsilon, eps))
