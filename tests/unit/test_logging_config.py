import logging

from search_engine.observability.logging_config import get_logger

def test_get_logger_returns_logger_with_correct_name():
    logger = get_logger("my.module.name")
    assert logger.name == "my.module.name"
    assert isinstance(logger, logging.Logger)

def test_repeated_calls_do_not_duplicate_handlers():
    get_logger("module.a")
    count_after_first = len(logging.getLogger().handlers)

    get_logger("module.b")
    get_logger("module.c")
    count_after_more_calls = len(logging.getLogger().handlers)

    assert count_after_more_calls == count_after_first

def test_log_level_defaults_to_info(monkeypatch):
    monkeypatch.delenv("SEARCH_ENGINE_LOG_LEVEL", raising=False)

    import search_engine.observability.logging_config as log_config

    log_config._CONFIGURED = False
    logging.getLogger().handlers.clear()

    get_logger("test.default.level")
    assert logging.getLogger().level == logging.INFO

def test_log_level_configurable_via_environment(monkeypatch):
    monkeypatch.setenv("SEARCH_ENGINE_LOG_LEVEL", "DEBUG")

    import search_engine.observability.logging_config as log_config

    log_config._CONFIGURED = False
    logging.getLogger().handlers.clear()

    get_logger("test.debug.level")
    assert logging.getLogger().level == logging.DEBUG

def test_invalid_log_level_falls_back_to_info(monkeypatch):
    monkeypatch.setenv("SEARCH_ENGINE_LOG_LEVEL", "NOT_A_REAL_LEVEL")

    import search_engine.observability.logging_config as log_config

    log_config._CONFIGURED = False
    logging.getLogger().handlers.clear()

    get_logger("test.invalid.level")
    assert logging.getLogger().level == logging.INFO