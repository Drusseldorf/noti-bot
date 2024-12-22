from app.db.base import Base
from datetime import datetime, UTC
from sqlalchemy import (
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Boolean,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


# TODO: В базу сейчас пишем не в utc все таки вроде, нужно проверить
class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None, microsecond=0),
    )
    user_timezone_offset: Mapped[int] = mapped_column(nullable=True)

    notification: Mapped[list["Notification"]] = relationship(
        back_populates="user"
    )


class Notification(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        ForeignKey("user.telegram_id"), nullable=False
    )
    notification_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None, microsecond=0),
    )
    event_time_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    notification_advance_time: Mapped[int] = mapped_column(nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="notification")

    __table_args__ = (
        CheckConstraint(
            "time_to_notify > NOW()", name="check_time_to_notify_at_future"
        ),
    )
