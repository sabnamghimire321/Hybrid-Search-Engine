class RobotsRules:
    def __init__(self) -> None:
        self.disallow: list[str] = []
        self.allow: list[str] = []
        self.crawl_delay: float | None = None

class RobotsParser:
    def __init__(self, robots_txt: str, user_agent: str = "*") -> None:
        self._user_agent = user_agent
        self._rules_by_agent = self._parse(robots_txt)

    def _parse(self, text: str) -> dict[str, RobotsRules]:
        rules_by_agent: dict[str, RobotsRules] = {}
        current_agents: list[str] = []
        current_block_has_rules = False

        for raw_line in text.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue

            field, _, value = line.partition(":")
            field = field.strip().lower()
            value = value.strip()

            if field == "user-agent":
                if current_block_has_rules or not current_agents:
                    current_agents = [value]
                    current_block_has_rules = False
                else:
                    current_agents.append(value)
                rules_by_agent.setdefault(value, RobotsRules())

            elif field == "disallow" and current_agents:
                current_block_has_rules = True
                if value:
                    for agent in current_agents:
                        rules_by_agent[agent].disallow.append(value)

            elif field == "allow" and current_agents:
                current_block_has_rules = True
                for agent in current_agents:
                    rules_by_agent[agent].allow.append(value)

            elif field == "crawl-delay" and current_agents:
                current_block_has_rules = True
                try:
                    delay = float(value)
                except ValueError:
                    delay = None
                for agent in current_agents:
                    rules_by_agent[agent].crawl_delay = delay

        return rules_by_agent

    def _rules_for_configured_agent(self) -> RobotsRules | None:
        return self._rules_by_agent.get(self._user_agent) or self._rules_by_agent.get("*")

    def is_allowed(self, path: str) -> bool:
        rules = self._rules_for_configured_agent()
        if rules is None:
            return True

        best_match_length = -1
        best_match_is_allow = True

        for pattern in rules.disallow:
            if path.startswith(pattern) and len(pattern) > best_match_length:
                best_match_length = len(pattern)
                best_match_is_allow = False

        for pattern in rules.allow:
            if path.startswith(pattern) and len(pattern) >= best_match_length:
                best_match_length = len(pattern)
                best_match_is_allow = True

        return best_match_is_allow

    @property
    def crawl_delay(self) -> float | None:
        rules = self._rules_for_configured_agent()
        return rules.crawl_delay if rules else None