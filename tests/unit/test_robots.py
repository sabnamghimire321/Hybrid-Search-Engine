from search_engine.crawler.robots import RobotsParser

def test_simple_disallow_blocks_path():
    robots_txt = """
User-agent: *
Disallow: /private/
"""
    parser = RobotsParser(robots_txt)
    assert parser.is_allowed("/private/secret.html") is False
    assert parser.is_allowed("/public/page.html") is True


def test_allow_overrides_more_general_disallow():
    robots_txt = """
User-agent: *
Disallow: /private/
Allow: /private/public-notice/
"""
    parser = RobotsParser(robots_txt)
    assert parser.is_allowed("/private/secret.html") is False
    assert parser.is_allowed("/private/public-notice/announcement.html") is True


def test_no_matching_rule_defaults_to_allowed():
    robots_txt = """
User-agent: *
Disallow: /admin/
"""
    parser = RobotsParser(robots_txt)
    assert parser.is_allowed("/completely/unrelated/path.html") is True


def test_empty_robots_txt_allows_everything():
    parser = RobotsParser("")
    assert parser.is_allowed("/anything") is True


def test_specific_user_agent_overrides_wildcard():
    robots_txt = """
User-agent: *
Disallow: /

User-agent: MyFriendlyBot
Disallow: /admin/
"""
    parser = RobotsParser(robots_txt, user_agent="MyFriendlyBot")
    assert parser.is_allowed("/public/page.html") is True
    assert parser.is_allowed("/admin/secret") is False


def test_falls_back_to_wildcard_when_no_specific_section():
    robots_txt = """
User-agent: *
Disallow: /private/
"""
    parser = RobotsParser(robots_txt, user_agent="SomeOtherBot")
    assert parser.is_allowed("/private/x") is False


def test_multiple_user_agents_share_one_block():
    robots_txt = """
User-agent: BotA
User-agent: BotB
Disallow: /shared-block/
"""
    parser_a = RobotsParser(robots_txt, user_agent="BotA")
    parser_b = RobotsParser(robots_txt, user_agent="BotB")

    assert parser_a.is_allowed("/shared-block/x") is False
    assert parser_b.is_allowed("/shared-block/x") is False


def test_crawl_delay_is_parsed():
    robots_txt = """
User-agent: *
Disallow: /admin/
Crawl-delay: 2.5
"""
    parser = RobotsParser(robots_txt)
    assert parser.crawl_delay == 2.5


def test_crawl_delay_absent_returns_none():
    robots_txt = """
User-agent: *
Disallow: /admin/
"""
    parser = RobotsParser(robots_txt)
    assert parser.crawl_delay is None


def test_comments_and_blank_lines_are_ignored():
    robots_txt = """
# This is a comment
User-agent: *  # inline comment too

Disallow: /private/
# another comment
"""
    parser = RobotsParser(robots_txt)
    assert parser.is_allowed("/private/x") is False
    assert parser.is_allowed("/public/x") is True