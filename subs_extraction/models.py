from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Staging comment has minimum integrity requirements: no FK constraints on post_id and parent_id columns. 
# Anticipation being is that this data has to be checked on integrity before moving to production table.
class CommentsStaging(Base):
    __tablename__ = 'comments_staging'

    comment_id = Column(String, primary_key=True)  # e.g., t1_xyz789
    post_id = Column(String, ForeignKey('posts.post_id'), nullable=False)
    parent_id = Column(String, nullable=False)  # could reference post_id or comment_id
    path = Column(Text)
    body = Column(Text, nullable=False, default='')
    author = Column(Text, nullable=False, default='')
    created_at = Column(DateTime, nullable=False)
    score = Column(Integer, nullable=False, default=0)
    depth = Column(Integer, nullable=False, default=0)

    # Optional relationships
    # post = relationship("Posts", back_populates="comments")  # If Posts model includes backref
    # parent_comment = relationship("Comments", remote_side=[comment_id], uselist=False)

    def __repr__(self):
        return f"<CommentsStaging(comment_id={self.comment_id}, author={self.author}, depth={self.depth})>"
