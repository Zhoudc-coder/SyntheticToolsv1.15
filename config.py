import os
import sys
import json
from pathlib import Path

CONFIG_FILENAME = "config.json"

def _get_default_log_dir() -> Path:
    """返回默认日志目录（统一为程序所在目录下的 merge_log）"""
    env_dir = os.environ.get('MERGE_LOG_DIR')
    if env_dir:
        return Path(env_dir)

    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent
    return base_dir / 'merge_log'

def _find_config_file() -> Path | None:
    """查找配置文件，返回存在的配置文件路径，否则返回 None"""
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
    else:
        exe_dir = Path(__file__).parent
    config_path = exe_dir / CONFIG_FILENAME
    if config_path.exists():
        return config_path

    home_config = Path.home() / CONFIG_FILENAME
    if home_config.exists():
        return home_config

    return None

def _load_config_log_dir() -> Path | None:
    """从配置文件读取 log_dir，如果有效返回 Path，否则返回 None"""
    config_path = _find_config_file()
    if not config_path:
        return None
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        log_dir_str = config.get('log_dir')
        if log_dir_str:
            return Path(log_dir_str)
    except Exception:
        pass
    return None

def _ensure_config_file(default_log_dir: Path):
    """如果配置文件不存在，则创建一个包含默认路径的配置文件"""
    if _find_config_file() is not None:
        return
    if getattr(sys, 'frozen', False):
        config_dir = Path(sys.executable).parent
    else:
        config_dir = Path(__file__).parent
    try:
        config_path = config_dir / CONFIG_FILENAME
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({"log_dir": str(default_log_dir)}, f, indent=4)
    except Exception:
        home_config = Path.home() / CONFIG_FILENAME
        try:
            with open(home_config, 'w', encoding='utf-8') as f:
                json.dump({"log_dir": str(default_log_dir)}, f, indent=4)
        except Exception:
            pass

def _get_log_dir() -> Path:
    """获取日志目录，优先级：环境变量 > 配置文件 > 默认路径"""
    env_dir = os.environ.get('MERGE_LOG_DIR')
    if env_dir:
        return Path(env_dir)

    config_dir = _load_config_log_dir()
    if config_dir:
        return config_dir

    return _get_default_log_dir()

LOG_DIR = _get_log_dir()
DB_PATH = LOG_DIR / 'merge_log.db'

RETENTION_DAYS = 15
XLSX_SUFFIX = '.xlsx'
CSV_SUFFIX = '.csv'

def ensure_log_dir() -> Path:
    """
    确保日志目录存在，若不存在则尝试创建。
    如果创建失败，抛出 RuntimeError 并附带详细说明。
    同时尝试创建配置文件（若不存在），方便用户修改路径。
    """
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(
            f"无法创建日志目录 {LOG_DIR}，请检查：\n"
            f"1. 路径是否正确（Z 盘是否已连接？）\n"
            f"2. 是否有写入权限\n"
            f"3. 可修改配置文件 config.json 中的 log_dir 项，或设置环境变量 MERGE_LOG_DIR\n"
            f"原始错误：{e}"
        )

    _ensure_config_file(LOG_DIR)

    return LOG_DIR