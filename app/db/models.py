from app.db.base import Base
from datetime import datetime
from sqlalchemy import Text, DateTime, func, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    telegram_id: Mapped[int] = mapped_column(primary_key=True)

    notification: Mapped[list["Notification"]] = relationship(back_populates="user")

    # TODO: не используется, убрать?
    def __repr__(self):
        return f"User(telegram_id={self.telegram_id}, notification={self.notification})"


# TODO: подумать над названиями атрибутов
class Notification(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    notification_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    time_to_notify: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    telegram_id: Mapped[int] = mapped_column(
        ForeignKey("user.telegram_id"), nullable=False
    )
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="notification")

    __table_args__ = (
        CheckConstraint(
            "time_to_notify > NOW()", name="check_time_to_notify_at_future"
        ),
    )
