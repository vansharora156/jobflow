from datetime import datetime


from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column


from app.database import Base




class JobDB(Base):
    __tablename__ = "jobs"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


    title: Mapped[str] = mapped_column(String(255), nullable=False)


    company: Mapped[str] = mapped_column(String(255), nullable=False)


    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True,
    )


    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
