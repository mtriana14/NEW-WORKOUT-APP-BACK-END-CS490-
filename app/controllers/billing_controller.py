from flask import request, jsonify
from app.config.db import db
from app.models.saved_billing import SavedBilling
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.coach import Coach
from app.models.hire import Hire
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, date
import uuid


def get_saved_cards():
    """
    Check saved payment methods of user 
    """
    user_id = int(get_jwt_identity())
    cards = SavedBilling.query.filter_by(user_id=user_id).order_by(
        SavedBilling.is_default.desc(), SavedBilling.created_at.desc()
    ).all()

    return jsonify({
        'cards': [
            {
                'card_id':      c.card_id,
                'last_four':    c.last_four,
                'card_brand':   c.card_brand,
                'expiry_month': c.expiry_month,
                'expiry_year':  c.expiry_year,
                'is_default':   c.is_default,
            }
            for c in cards
        ]
    }), 200


def add_saved_card():
    """
    let user add a new billing method, can set it to default payment method
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    last_four    = data.get('last_four')
    expiry_month = data.get('expiry_month')
    expiry_year  = data.get('expiry_year')

    if not all([last_four, expiry_month, expiry_year]):
        return jsonify({'error': 'last_four, expiry_month, and expiry_year are required'}), 400

    is_default = data.get('is_default', False)

    if is_default:
        SavedBilling.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})

    card = SavedBilling(
        user_id      = user_id,
        last_four    = str(last_four)[-4:],
        card_brand   = data.get('card_brand'),
        expiry_month = expiry_month,
        expiry_year  = expiry_year,
        is_default   = is_default,
    )
    db.session.add(card)
    db.session.commit()

    return jsonify({
        'message': 'Card saved successfully',
        'card_id': card.card_id
    }), 201


def delete_saved_card(card_id):
    """
    Let user delete any saved payment methods if needed
    """
    user_id = int(get_jwt_identity())

    card = SavedBilling.query.filter_by(card_id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404

    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': 'Card removed successfully'}), 200


def pay_with_saved_card(coach_id):
    """
    pay a subscription with a coach with a saved card, this is after client already
    subscribed, this would be for recurring payments or paying it manually using a stored payment method 
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json() or {}

    card_id = data.get('card_id')
    if not card_id:
        return jsonify({'error': 'card_id is required'}), 400

    # Verify card belongs to user
    card = SavedBilling.query.filter_by(card_id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Saved card not found'}), 404

    # Verify active hire
    hire = Hire.query.filter_by(user_id=user_id, coach_id=coach_id, status='active').first()
    if not hire:
        return jsonify({'error': 'No active coaching relationship found with this coach'}), 400

    # Verify active subscription
    subscription = Subscription.query.filter_by(
        user_id=user_id, coach_id=coach_id, status='active'
    ).first()
    if not subscription:
        return jsonify({'error': 'No active subscription found with this coach'}), 400

    # Create payment record
    payment = Payment(
        client_id           = user_id,
        coach_id            = coach_id,
        subscription_id     = subscription.subscription_id,
        card_id             = card.card_id,
        amount              = subscription.amount,
        currency            = 'USD',
        payment_method_type = 'credit_card',
        status              = 'completed',
        transaction_id      = str(uuid.uuid4()),
        description         = f'Subscription payment via saved card ending in {card.last_four}',
        paid_at             = datetime.utcnow(),
    )
    db.session.add(payment)

    # Advance next billing date by one month
    nb = subscription.next_billing or date.today()
    next_month = nb.month % 12 + 1
    next_year  = nb.year + (1 if nb.month == 12 else 0)
    try:
        subscription.next_billing = date(next_year, next_month, nb.day)
    except ValueError:
        import calendar
        last_day = calendar.monthrange(next_year, next_month)[1]
        subscription.next_billing = date(next_year, next_month, last_day)

    db.session.commit()

    return jsonify({
        'message':        'Payment successful',
        'payment_id':     payment.payment_id,
        'transaction_id': payment.transaction_id,
        'amount':         float(payment.amount),
        'card_used':      f'{card.card_brand} ending in {card.last_four}',
        'next_billing':   str(subscription.next_billing),
    }), 201