from flask import request, jsonify
from app.config.db import db
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.hire import Hire
from app.models.coach import Coach
from app.models.saved_billing import SavedBilling
from app.models.notification import Notification
from flask_jwt_extended import get_jwt_identity
from datetime import date, datetime
import uuid

def subscribe_to_coach(coach_id):
    """Subscribe to a coach - create subscription and process payment."""
    user_id = int(get_jwt_identity())

    # Check there is an active hire with this coach
    hire = Hire.query.filter_by(
        user_id=user_id,
        coach_id=coach_id,
        status='active'
    ).first()
    if not hire:
        return jsonify({'error': 'You must have an accepted coaching request before subscribing'}), 400

    # Check if already subscribed
    existing = Subscription.query.filter_by(
        user_id=user_id,
        coach_id=coach_id,
        status='active'
    ).first()
    if existing:
        return jsonify({'error': 'You already have an active subscription with this coach'}), 409

    # Get coach for cost
    coach = Coach.query.get(coach_id)
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404

    data = request.get_json()

    # Check if using saved card or new card
    card_id = data.get('card_id')
    if card_id:
        # Use saved card
        card = SavedBilling.query.filter_by(
            card_id=card_id,
            user_id=user_id
        ).first()
        if not card:
            return jsonify({'error': 'Saved card not found'}), 404
    else:
        # New card — save it if requested
        save_card = data.get('save_card', False)
        last_four = data.get('last_four')
        card_brand = data.get('card_brand')
        expiry_month = data.get('expiry_month')
        expiry_year = data.get('expiry_year')

        if not all([last_four, expiry_month, expiry_year]):
            return jsonify({'error': 'Card details are required'}), 400

        if save_card:
            card = SavedBilling(
                user_id=user_id,
                last_four=last_four,
                card_brand=card_brand,
                expiry_month=expiry_month,
                expiry_year=expiry_year,
                is_default=data.get('is_default', False)
            )
            db.session.add(card)
            db.session.flush()
            card_id = card.card_id
        else:
            card_id = None

    # Create subscription
    today = date.today()
    next_month = today.month % 12 + 1
    next_year = today.year + (1 if today.month == 12 else 0)
    next_billing_date = date(next_year, next_month, today.day)

    subscription = Subscription(
        user_id=user_id,
        coach_id=coach_id,
        plan_type=data.get('plan_type', 'Monthly'),
        amount=coach.cost,
        status='active',
        start_date=today,
        next_billing=next_billing_date
        
    )
    db.session.add(subscription)
    db.session.flush()

    # Create payment record
    payment = Payment(
        client_id=user_id,
        coach_id=coach_id,
        subscription_id=subscription.subscription_id,
        card_id=card_id,
        amount=coach.cost,
        currency='USD',
        payment_method_type='credit_card',
        status='completed',
        transaction_id=str(uuid.uuid4()),
        description=f'Monthly coaching subscription',
        paid_at=datetime.utcnow()
    )
    db.session.add(payment)

    # Notify the coach that client has subbed
    notification = Notification(
        user_id=coach.user_id,
        title='New Subscription',
        message='A client has subscribed to your coaching services.',
        type='payment'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Successfully subscribed to coach',
        'subscription_id': subscription.subscription_id,
        'amount': float(coach.cost),
        'plan_type': subscription.plan_type,
        'start_date': str(subscription.start_date),
        'next_billing': str(subscription.next_billing)
    }), 201