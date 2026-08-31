from search_engine.crawler.scheduler import CrawlScheduler

def test_first_fetch_to_a_domain_requires_no_wait():
    scheduler = CrawlScheduler(default_delay=1.0)
    assert scheduler.time_until_allowed("example.com", current_time=100.0) == 0.0

def test_immediate_recheck_requires_waiting_full_delay():
    scheduler = CrawlScheduler(default_delay=2.0)
    scheduler.record_fetch("example.com", current_time=100.0)

    assert scheduler.time_until_allowed("example.com", current_time=100.0) == 2.0

def test_partial_elapsed_time_returns_remaining_wait():
    scheduler = CrawlScheduler(default_delay=2.0)
    scheduler.record_fetch("example.com", current_time=100.0)

    remaining = scheduler.time_until_allowed("example.com", current_time=101.5)
    assert remaining == 0.5

def test_sufficient_elapsed_time_requires_no_wait():
    scheduler = CrawlScheduler(default_delay=2.0)
    scheduler.record_fetch("example.com", current_time=100.0)

    assert scheduler.time_until_allowed("example.com", current_time=103.0) == 0.0

def test_domain_specific_delay_overrides_default():
    scheduler = CrawlScheduler(default_delay=1.0)
    scheduler.set_domain_delay("slow-site.com", delay=5.0)

    assert scheduler.delay_for("slow-site.com") == 5.0
    assert scheduler.delay_for("other-site.com") == 1.0

def test_different_domains_are_tracked_independently():
    scheduler = CrawlScheduler(default_delay=2.0)
    scheduler.record_fetch("site-a.com", current_time=100.0)

    assert scheduler.time_until_allowed("site-b.com", current_time=100.0) == 0.0
    assert scheduler.time_until_allowed("site-a.com", current_time=100.0) == 2.0

def test_wait_if_needed_actually_sleeps_and_updates_state():
    scheduler = CrawlScheduler(default_delay=0.01)

    first_wait = scheduler.wait_if_needed("example.com")
    assert first_wait == 0.0

    second_wait = scheduler.wait_if_needed("example.com")
    assert second_wait > 0.0