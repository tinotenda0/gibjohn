from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Enum as SAEnum
from flask_login import UserMixin
from hashlib import md5
from enum import Enum


class Base(DeclarativeBase):
    pass
# Defining user roles
class Roles(Enum):
    tutor = 'tutor'
    student = 'student'

# Defining the user model
class User(UserMixin, Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # Using gravatar for profile pictures instead of storing images
    def gravatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Using enum for user roles since we only have two fixed roles
    role: Mapped[Roles] = mapped_column(SAEnum(Roles, name="urole", native_enum=False),nullable=False,default=Roles.student)

    def __repr__(self):
        return f"<User {self.email}>"


class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self):
        return f"<Course {self.title}>"

    def __repr__(self):
        return f"<Assignment {self.title} for Course ID: {self.course_id}>"

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self):
        return f"<Enrollment User ID: {self.user_id}, Course ID: {self.course_id}>"