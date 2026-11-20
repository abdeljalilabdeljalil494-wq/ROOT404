"""Activity aggregates derived exclusively from persisted submission timestamps."""
from collections import Counter
from datetime import datetime, timedelta
from app.models.submission import Submission


def daily_counts(db, user_id, days):
    start = datetime.combine(datetime.utcnow().date() - timedelta(days=days - 1), datetime.min.time())
    rows = db.query(Submission.created_at).filter(Submission.user_id == user_id, Submission.created_at >= start).all()
    counts = Counter(row[0].date() for row in rows)
    return [(start.date() + timedelta(days=i), counts[start.date() + timedelta(days=i)]) for i in range(days)]
