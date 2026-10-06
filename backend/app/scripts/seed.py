"""Run from backend/: python -m app.scripts.seed"""

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Account, User, Vpc


def seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        account = db.scalar(
            select(Account).where(Account.aws_account_id == "610867948442")
        )
        if not account:
            account = Account(
                aws_account_id="610867948442",
                display_name="zulu",
                default_region="us-east-1",
            )
            db.add(account)
            db.flush()
        if not db.scalar(select(User).where(User.email == "student@example.com")):
            db.add(
                User(
                    account_id=account.id,
                    email="student@example.com",
                    display_name="student-57",
                    password_hash=hash_password("Password123!"),
                )
            )
        if not db.scalar(
            select(Vpc).where(
                Vpc.account_id == account.id, Vpc.aws_vpc_id == "vpc-08750f9ac60190242"
            )
        ):
            db.add(
                Vpc(
                    account_id=account.id,
                    aws_vpc_id="vpc-08750f9ac60190242",
                    region="us-east-1",
                    name="Route53 demo VPC",
                )
            )
        db.commit()
    print("Seeded student@example.com / Password123!")


if __name__ == "__main__":
    seed()
