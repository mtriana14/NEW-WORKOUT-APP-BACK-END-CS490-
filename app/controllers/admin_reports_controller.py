from flask import request, jsonify
from app.config.db import db
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.models.checkin import Check_in as Checkin
from sqlalchemy import func, distinct, or_
from datetime import date, datetime, timedelta


def _period_bounds(period):
    """Return (start_date, end_date, bucket_format) for daily|weekly|monthly."""
    today = date.today()
    if period == 'daily':
        start = today - timedelta(days=29)    # last 30 days, bucketed per day
        fmt = '%Y-%m-%d'
    elif period == 'weekly':
        start = today - timedelta(weeks=11)   # ~12 weeks back
        fmt = '%Y-W%V'                         # ISO week
    elif period == 'monthly':
        # Last 12 months (approx — 365 days back)
        start = today - timedelta(days=365)
        fmt = '%Y-%m'
    else:
        start = today - timedelta(days=29)
        fmt = '%Y-%m-%d'
    return start, today, fmt


def _bucket_key(d, period):
    """Convert a date into the bucket key matching the format used in the report."""
    if period == 'daily':
        return d.isoformat()
    if period == 'weekly':
        iso_year, iso_week, _ = d.isocalendar()
        return f'{iso_year}-W{iso_week:02d}'
    if period == 'monthly':
        return f'{d.year:04d}-{d.month:02d}'
    return d.isoformat()


def _all_bucket_keys(start, end, period):
    """Enumerate all bucket keys between start and end so the graph has no gaps."""
    keys = []
    if period == 'daily':
        cur = start
        while cur <= end:
            keys.append(cur.isoformat())
            cur += timedelta(days=1)
    elif period == 'weekly':
        cur = start
        seen = set()
        while cur <= end:
            k = _bucket_key(cur, 'weekly')
            if k not in seen:
                keys.append(k)
                seen.add(k)
            cur += timedelta(days=1)
    elif period == 'monthly':
        y, m = start.year, start.month
        while (y, m) <= (end.year, end.month):
            keys.append(f'{y:04d}-{m:02d}')
            m += 1
            if m > 12:
                m = 1
                y += 1
    return keys


def get_active_users_report():
    """
    GET /api/admin/reports/active-users?period=daily|weekly|monthly

    "Active" = a user who has either logged an activity OR submitted a check-in
    OR logged into the platform in that bucket. We dedupe by user_id per bucket.

    Response includes:
      - totals: total users, currently active, deactivated
      - buckets: [{ bucket: 'YYYY-MM-DD', active_users: N, new_signups: N }, ...]
    """
    period = (request.args.get('period') or 'daily').lower()
    if period not in ('daily', 'weekly', 'monthly'):
        return jsonify({'error': "period must be 'daily', 'weekly', or 'monthly'"}), 400

    start, end, _ = _period_bounds(period)
    start_dt = datetime.combine(start, datetime.min.time())

    # --- Pull raw activity within the period -------------------------------
    # Activity log dates
    act_rows = (
        db.session.query(ActivityLog.user_id, ActivityLog.log_date)
        .filter(ActivityLog.is_deleted == False)  # noqa: E712
        .filter(ActivityLog.log_date >= start)
        .all()
    )

    # Check-in dates (created_at is a datetime)
    try:
        ci_rows = (
            db.session.query(Checkin.user_id, Checkin.created_at)
            .filter(Checkin.created_at >= start_dt)
            .all()
        )
    except Exception:
        # Checkin model might have a different column name in some branches
        ci_rows = []

    # Last-login touches (rough proxy for "opened the app")
    login_rows = (
        db.session.query(User.user_id, User.last_login)
        .filter(User.last_login != None)  # noqa: E711
        .filter(User.last_login >= start_dt)
        .all()
    )

    # New signups for the "new_signups" sub-metric
    signup_rows = (
        db.session.query(User.user_id, User.created_at)
        .filter(User.created_at >= start_dt)
        .all()
    )

    # --- Bucket them -------------------------------------------------------
    bucket_keys = _all_bucket_keys(start, end, period)
    active_by_bucket = {k: set() for k in bucket_keys}
    signups_by_bucket = {k: 0 for k in bucket_keys}

    def _touch(uid, ts):
        if ts is None:
            return
        d = ts.date() if isinstance(ts, datetime) else ts
        if d < start or d > end:
            return
        key = _bucket_key(d, period)
        if key in active_by_bucket:
            active_by_bucket[key].add(uid)

    for uid, d in act_rows:
        _touch(uid, d)
    for uid, d in ci_rows:
        _touch(uid, d)
    for uid, d in login_rows:
        _touch(uid, d)

    for uid, ts in signup_rows:
        if ts is None:
            continue
        d = ts.date() if isinstance(ts, datetime) else ts
        if d < start or d > end:
            continue
        key = _bucket_key(d, period)
        if key in signups_by_bucket:
            signups_by_bucket[key] += 1

    # --- Totals ------------------------------------------------------------
    total_users     = db.session.query(func.count(User.user_id)).scalar() or 0
    active_accounts = db.session.query(func.count(User.user_id)).filter(User.is_active == True).scalar() or 0  # noqa: E712
    deactivated     = total_users - active_accounts

    buckets = [
        {
            'bucket':       k,
            'active_users': len(active_by_bucket[k]),
            'new_signups':  signups_by_bucket[k],
        }
        for k in bucket_keys
    ]

    # Peak bucket
    peak = max(buckets, key=lambda b: b['active_users']) if buckets else None

    return jsonify({
        'period':     period,
        'start_date': start.isoformat(),
        'end_date':   end.isoformat(),
        'totals': {
            'total_users':     int(total_users),
            'active_accounts': int(active_accounts),
            'deactivated':     int(deactivated),
        },
        'peak_bucket': peak,
        'buckets':     buckets,
    }), 200


def get_role_breakdown_report():
    """GET /api/admin/reports/roles — quick counts by role & status."""
    rows = (
        db.session.query(User.role, User.is_active, func.count(User.user_id))
        .group_by(User.role, User.is_active)
        .all()
    )
    result = {}
    for role, is_active, count in rows:
        result.setdefault(role, {'active': 0, 'deactivated': 0})
        if is_active:
            result[role]['active'] += int(count)
        else:
            result[role]['deactivated'] += int(count)
    return jsonify({'by_role': result}), 200
