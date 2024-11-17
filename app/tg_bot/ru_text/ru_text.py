from pathlib import Path
from pydantic_settings_yaml import YamlBaseSettings
import warnings

warnings.filterwarnings("ignore")

TEXT_PATH = Path(__file__).parent.joinpath("ru_text.yaml")


class Text(YamlBaseSettings):
    start_greeting: str
    edit_txt: str
    cancel_wrong: str
    no_timezone: str
    cancel: str
    no_notifications_yet: str
    notifications: str
    user_timezone_set: str
    notification_advance_time: str
    fill_date_and_time: str
    date_in_past: str
    fill_notification_text: str
    wrong_date_format: str
    notification_created: str
    something_went_wrong: str

    class Config:
        yaml_file = TEXT_PATH


ru_message = Text()
