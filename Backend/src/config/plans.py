"""
Plan configuration for the Marketing Agent application.
This file centralizes all plan definitions to make them easy to manage and update.
"""

# Available subscription plans
AVAILABLE_PLANS = {
    'pro_plan': {
        'id': 'pro_plan',
        'name': 'Pro Plan - Marketing Agent',
        'price': '19.99',
        'currency': 'TL',
        'quantity': 1,
        'description': 'Everything you need to generate leads at scale',
        'features': [
            'Unlimited AI content generation',
            'Advanced lead generation tools', 
            'Priority support',
            'Analytics dashboard'
        ]
    }
}

def get_plan(plan_id: str) -> dict:
    """Get plan details by ID"""
    return AVAILABLE_PLANS.get(plan_id)

def get_all_plans() -> dict:
    """Get all available plans"""
    return AVAILABLE_PLANS.copy()

def is_valid_plan(plan_id: str) -> bool:
    """Check if a plan ID is valid"""
    return plan_id in AVAILABLE_PLANS
